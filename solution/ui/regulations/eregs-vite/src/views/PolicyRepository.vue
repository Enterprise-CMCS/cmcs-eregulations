<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isEmpty from "lodash/isEmpty";

import { getSubjectName } from "utilities/filters";

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
    paramsArray: [],
});

const updateSelectedParams = (paramArgs) => {
    const { action, id, name, type } = paramArgs;

    // early return if the param is already selected
    if (selectedParams.paramString.includes(`${type}=${id}`)) return;

    // update paramString that is used as reactive prop for watch
    if (selectedParams.paramString) {
        selectedParams.paramString += `&${type}=${id}`;
    } else {
        selectedParams.paramString = `?${type}=${id}`;
    }

    // create new selectedParams key for array of objects for selections
    selectedParams.paramsArray.push({ id, name, type });
};

provide("selectedParams", selectedParams);

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
                    id: subject.id,
                    name: getSubjectName(subject),
                });
            });

            getDocList(getRequestParams($route.query));
        }
    }
};

watch(
    () => $route.query,
    async (newParams, oldParams) => {
        if (newParams.subjects) {
            const subjectIds = newParams.subjects.split(",");
            const subjects = policyDocSubjects.value.results.filter((subject) =>
                subjectIds.includes(subject.id.toString())
            );

            subjects.forEach((subject) => {
                updateSelectedParams({
                    type: "subjects",
                    id: subject.id,
                    name: getSubjectName(subject),
                });
            });
        }

        // parse $route.query to return `${key}=${value}` string
        const newRequestParams = getRequestParams(newParams);

        await getDocList(newRequestParams);
    }
);

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
