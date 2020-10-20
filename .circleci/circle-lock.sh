#!/usr/bin/env bash

set -o xtrace -o errexit -o pipefail -o nounset

########################################################################################
# CircleCI's current recommendation for roughly serializing a subset
# of build commands for a given branch
#
# circle discussion thread - https://discuss.circleci.com/t/serializing-deployments/153
# Code from - https://github.com/bellkev/circle-lock-test
########################################################################################


# sets $branch, $job_name, $tag, $rest
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--branch) branch="$2" ;;
            -j|--job-name) job_name="$2" ;;
            -t|--tag) tag="$2" ;;
            *) break ;;
        esac
        shift 2
    done
    rest=("$@")
}

# reads $branch, $tag, $commit_message
should_skip() {
    if [[ "$branch" && "$CIRCLE_BRANCH" != "$branch" ]]; then
        echo "Not on branch $branch. Skipping..."
        return 0
    fi

    if [[ "$job_name" && "$CIRCLE_JOB" != "$job_name" ]]; then
        echo "Not running $job_name. Skipping..."
        return 0
    fi

    if [[ "$tag" && "$commit_message" != *\[$tag\]* ]]; then
        echo "No [$tag] commit tag found. Skipping..."
        return 0
    fi

    return 1
}

# reads $branch, $job_name, $tag
# sets $jq_prog
make_jq_prog() {
    local jq_filters=""

    if [[ $branch ]]; then
        jq_filters+=" and .branch == \"$branch\""
    fi

    if [[ $job_name ]]; then
        jq_filters+=" and (.workflows?.job_name? == \"$job_name\" or .build_parameters?.CIRCLE_JOB? == \"$job_name\")"
    fi

    if [[ $tag ]]; then
        jq_filters+=" and (.subject | contains(\"[$tag]\"))"
    fi

    jq_prog=".[] | select(.build_num < $CIRCLE_BUILD_NUM and (.status | test(\"running|pending|queued\")) $jq_filters) | .build_num"
}


if [[ "$0" != *bats* ]]; then
    set -e
    set -u
    set -o pipefail

    branch=""
    tag=""
    job_name=""
    rest=()
    circle_base_url=`echo ${CIRCLE_BUILD_URL##https://} | cut -d/ -f1`
    api_url="https://$circle_base_url/api/v1/project/$CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME?circle-token=$CIRCLE_TOKEN&limit=100"

    parse_args "$@"
    commit_message=$(git log -1 --pretty=%B)
    if should_skip; then exit 0; fi
    make_jq_prog

    echo "Checking for running builds..."

    # unset errexit so we can detect and handle temporary circleci api failures
    set +e
    consecutive_failures=0
    while true;  do
        builds=$(curl --fail --silent --connect-timeout 5 --max-time 10 -H "Accept: application/json" "$api_url" | jq "$jq_prog")

        if [[ $? -ne 0 ]]; then
            echo "CircleCI api call failed"
            consecutive_failures=$(($consecutive_failures + 1))
        elif [[ ! -z ${builds} ]]; then
            # reset failure counter
            consecutive_failures=0

            echo "Waiting on builds:"
            echo "$builds"
        else
            break
        fi

        # limit the number of consecutive failures that we're willing to tolerate
        if [[ ${consecutive_failures} -gt 5 ]]; then
            echo "Failed $consecutive_failures consecutive attempts...giving up"
            exit 1
        fi

        echo "Retrying in 10 seconds..."
        sleep 10
    done

    echo "Acquired lock"
fi
