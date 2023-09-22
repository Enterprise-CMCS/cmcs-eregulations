<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isEmpty from "lodash/isEmpty";

import {
    getLastUpdatedDates,
    getPolicyDocList,
    getPolicyDocSubjects,
    getTitles,
} from "utilities/api";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import PolicyResults from "@/components/policy-repository/PolicyResults.vue";
import PolicySelections from "@/components/policy-repository/PolicySelections.vue";
import PolicySidebar from "@/components/policy-repository/PolicySidebar.vue";
import SubjectSelector from "@/components/policy-repository/SubjectSelector.vue";

const props = defineProps({
    aboutUrl: {
        type: String,
        default: "/about/",
    },
    apiUrl: {
        type: String,
        default: "/v3/",
    },
    homeUrl: {
        type: String,
        default: "/",
    },
    resourcesUrl: {
        type: String,
        default: "/resources/",
    },
    searchUrl: {
        type: String,
        default: "/search/",
    },
    statutesUrl: {
        type: String,
        default: "/statutes/",
    },
    isAuthenticated: {
        type: Boolean,
        default: false,
    },
});

// Router and Route
const $router = useRouter();
const $route = useRoute();

// provide Django template variables
provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);

// partsLastUpdated fetch for related regulations citations filtering
const partsLastUpdated = ref({
    results: {},
    loading: true,
});

const getPartsLastUpdated = async () => {
    try {
        const titles = await getTitles();
        partsLastUpdated.value.results = await getLastUpdatedDates(
            props.apiUrl,
            titles
        );
    } catch (error) {
        console.error(error);
    } finally {
        partsLastUpdated.value.loading = false;
    }
};

// policyDocList fetch for policy document list
const policyDocList = ref({
    results: [],
    loading: true,
});

const getDocList = async (requestParams = "") => {
    try {
        policyDocList.value.results = await getPolicyDocList({
            apiUrl: props.apiUrl,
            cacheResponse: !props.isAuthenticated,
            requestParams,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocList.value.loading = false;
    }
};

// use reactive to make urlParams reactive when provided/injected
const selectedParams = reactive({
    paramString: "",
    queryParamsToSet: {},
    paramsArray: [],
});

const updateSelectedParams = (paramArgs) => {
    const { action, id, name, type } = paramArgs;

    // early return if removing a selected param
    if (action === "remove") {
        // early return if removing a param that is not selected
        if (!selectedParams.queryParamsToSet[type]) return;

        // remove from selectedParams.paramString
        const stringToEdit = selectedParams.paramString
            .substring(1)
            .split("&")
            .filter((param) => param !== `${type}=${id}`)
            .join("&");

        selectedParams.paramString = `?${stringToEdit}`;

        // remove from selectedParams.queryParamsToSet
        selectedParams.queryParamsToSet[type] = selectedParams.queryParamsToSet[
            type
        ]
            .split(",")
            .filter((param) => param !== id)
            .join(",");

        // remove from selectedParams.queryParamsToSet if empty
        if (!selectedParams.queryParamsToSet[type]) {
            delete selectedParams.queryParamsToSet[type];
        }

        // remove from selectedParams.paramsArray
        selectedParams.paramsArray = selectedParams.paramsArray.filter(
            (param) => param.id !== id
        );

        return;
    }

    // early return if the param is already selected
    if (
        action === "add" &&
        selectedParams.paramString.includes(`${type}=${id}`)
    )
        return;

    // update paramString that is used as reactive prop for watch
    if (selectedParams.paramString) {
        selectedParams.paramString += `&${type}=${id}`;
    } else {
        selectedParams.paramString = `?${type}=${id}`;
    }

    // update queryParamsToSet that is used to update the url
    if (selectedParams.queryParamsToSet[type]) {
        selectedParams.queryParamsToSet[type] += `,${id}`;
    } else {
        selectedParams.queryParamsToSet[type] = `${id}`;
    }

    // create new selectedParams key for array of objects
    selectedParams.paramsArray.push({ id, name, type });
};

provide("selectedParams", {
    selectedParams,
    updateSelectedParams,
});

// watch for changes to selectedParams.paramString and update url
watch(
    () => selectedParams.paramString,
    async () => {
        $router.push({
            name: "policy-repository",
            query: { ...selectedParams.queryParamsToSet },
        });
    }
);

// utility method to parse $route.query to return `${key}=${value},${value}` string
const getRequestParams = (query) => {
    const requestParams = Object.entries(query)
        .map(([key, value]) => {
            const valueArray = value.split(",");
            return valueArray.map((v) => `${key}=${v}`).join("&");
        })
        .join("&");

    return requestParams;
};

// watch for changes to url and fetch new results
watch(
    () => $route.query,
    async (newParams) => {
        // parse $route.query to return `${key}=${value}` string
        const requestParams = getRequestParams(newParams);
        await getDocList(requestParams);
    }
);

// policyDocSubjects fetch for subject selector
// fetch here so we have it in context; pass down to selector via props
const policyDocSubjects = ref({
    results: [],
    loading: true,
});

const getDocSubjects = async () => {
    try {
        policyDocSubjects.value.results = await getPolicyDocSubjects({
            apiUrl: props.apiUrl,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;

        // if there's a $route, call updateSelectedParams
        if (!_isEmpty($route.query)) {
            const subjectIds = $route.query.subjects.split(",");
            const subjects = policyDocSubjects.value.results.filter((subject) =>
                subjectIds.includes(subject.id.toString())
            );

            subjects.forEach((subject) => {
                updateSelectedParams({
                    type: "subjects",
                    action: "add",
                    id: subject.id,
                    name:
                        subject.short_name ||
                        subject.abbreviation ||
                        subject.full_name,
                });
            });

            getDocList(getRequestParams($route.query));
        }
    }
};

getDocSubjects();

getPartsLastUpdated();
getDocSubjects();

if (_isEmpty($route.query)) {
    getDocList();
}
</script>

<template>
    <body class="ds-base policy-repository-page">
        <BlockingModal>
            <IFrameContainer
                src="https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
                title="Google Forms iframe"
            />
        </BlockingModal>
        <FlashBanner />
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :about-url="aboutUrl"
                        :resources-url="resourcesUrl"
                        :statutes-url="statutesUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="policyRepositoryApp" class="repository-view ds-l-container">
            <div class="ds-l-row">
                <div
                    class="ds-l-col--12 ds-l-md-col--4 ds-l-lg-col--3 sidebar__container"
                >
                    <PolicySidebar>
                        <template #title>
                            <h2>Find Policy Documents</h2>
                        </template>
                        <template #selections>
                            <PolicySelections />
                        </template>
                        <template #filters>
                            <SubjectSelector
                                :policy-doc-subjects="policyDocSubjects"
                            />
                        </template>
                    </PolicySidebar>
                </div>
                <div class="ds-l-col--12 ds-l-md-col--8 ds-l-lg-col--9">
                    <template
                        v-if="policyDocList.loading || partsLastUpdated.loading"
                    >
                        <p>Loading...</p>
                    </template>
                    <template v-else>
                        <PolicyResults
                            :base="homeUrl"
                            :results="policyDocList.results"
                            :parts-last-updated="partsLastUpdated.results"
                        />
                    </template>
                </div>
            </div>
        </div>
    </body>
</template>
