<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router/composables";

import _difference from "lodash/difference";
import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";

import {
    getLastUpdatedDates,
    getPolicyDocList,
    getPolicyDocSubjects,
    getTitles,
} from "utilities/api";

import { getSubjectName, sortSubjects } from "utilities/filters";

import { getRequestParams } from "utilities/utils";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import PolicyResults from "@/components/policy-repository/PolicyResults.vue";
import PolicySelections from "@/components/policy-repository/PolicySelections.vue";
import PolicySidebar from "@/components/policy-repository/PolicySidebar.vue";
import SearchInput from "@/components/SearchInput.vue";
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
const $route = useRoute();
const $router = useRouter();

const FilterTypesDict = {
    subjects: "Subject",
    q: "query",
};

// provide Django template variables
provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);
provide("FilterTypesDict", FilterTypesDict);

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
    policyDocList.value.loading = true;

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

// use "reactive" method to make urlParams reactive when provided/injected
// selectedParams.paramString is used as the reactive prop
const selectedParams = reactive({
    paramString: "",
    paramsArray: [],
});

// method to add selected params
const addSelectedParams = (paramArgs) => {
    const { id, name, type } = paramArgs;

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

// method to remove selected params
const removeSelectedParams = (paramArgs) => {
    const { id, type } = paramArgs;

    // update paramString that is used as reactive prop for watch
    const paramStringArray = selectedParams.paramString.split("&");
    const paramString = paramStringArray
        .filter((param) => !param.includes(`${type}=${id}`))
        .join("&");

    selectedParams.paramString = paramString;

    // create new selectedParams key for array of objects for selections
    selectedParams.paramsArray = selectedParams.paramsArray.filter(
        (param) => param.id != id
    );
};

const clearSelectedParams = () => {
    selectedParams.paramString = "";
    selectedParams.paramsArray = [];
};

provide("selectedParams", selectedParams);

// policyDocSubjects fetch for subject selector
// fetch here so we have it in context; pass down to selector via props
const policyDocSubjects = ref({
    results: [],
    loading: true,
});

// called on load
const getDocSubjects = async () => {
    try {
        const subjectsResponse = await getPolicyDocSubjects({
            apiUrl: props.apiUrl,
        });

        policyDocSubjects.value.results = subjectsResponse.sort(sortSubjects);
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;

        // if there's a $route, call addSelectedParams
        if (!_isEmpty($route.query)) {
            const subjects = _isArray($route.query.subjects)
                ? $route.query.subjects[0]
                : $route.query.subjects;

            const subjectIds = subjects ? subjects.split(",") : [];
            const filteredSubjects = policyDocSubjects.value.results.filter(
                (subject) => subjectIds.includes(subject.id.toString())
            );

            filteredSubjects.forEach((subject) => {
                addSelectedParams({
                    type: "subjects",
                    id: subject.id,
                    name: getSubjectName(subject),
                });
            });

            getDocList(getRequestParams($route.query));
        }
    }
};

const executeSearch = (payload) => {
    $router.push({
        name: "policy-repository",
        query: {
            ...$route.query,
            q: payload.query,
        },
    });
};

const clearSearchQuery = () => {
    $router.push({
        name: "policy-repository",
        query: {
            ...$route.query,
            q: undefined,
        },
    });
};

watch(
    () => $route.query,
    async (newQueryParams, oldQueryParams) => {
        // if all params are removed, clear selectedParams and getDocList
        if (_isEmpty(newQueryParams)) {
            clearSelectedParams();
            getDocList();
            return;
        }

        // if there are multiple subjects already selected and one needs to be removed
        if (
            newQueryParams.subjects &&
            oldQueryParams.subjects &&
            newQueryParams.subjects.length < oldQueryParams.subjects.length
        ) {
            const oldSubjectIds = oldQueryParams.subjects.filter(
                (id) => !Number.isNaN(parseInt(id, 10))
            );
            const newSubjectIds = newQueryParams.subjects.filter(
                (id) => !Number.isNaN(parseInt(id, 10))
            );

            const subjectToRemove = _difference(oldSubjectIds, newSubjectIds);

            removeSelectedParams({
                type: "subjects",
                id: subjectToRemove[0],
            });

            const newRequestParams = getRequestParams(newQueryParams);
            await getDocList(newRequestParams);

            return;
        }

        if (newQueryParams.subjects) {
            const subjectsArray = _isArray(newQueryParams.subjects)
                ? newQueryParams.subjects
                : [newQueryParams.subjects];
            const subjectIds = subjectsArray.filter(
                (id) => !Number.isNaN(parseInt(id, 10))
            );
            const subjects = policyDocSubjects.value.results.filter((subject) =>
                subjectIds.includes(subject.id.toString())
            );

            subjects.forEach((subject) => {
                addSelectedParams({
                    type: "subjects",
                    id: subject.id,
                    name: getSubjectName(subject),
                });
            });
        }

        // parse $route.query to return `${key}=${value}` string
        const newRequestParams = getRequestParams(newQueryParams);
        await getDocList(newRequestParams);
    }
);

// fetches on page load
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
                    <button class="sidebar-toggle__button">Open/Close</button>
                    <PolicySidebar>
                        <template #title>
                            <h2>Find Policy Documents</h2>
                        </template>
                        <template #selections>
                            <PolicySelections />
                        </template>
                        <template #search>
                            <SearchInput
                                form-class="search-form"
                                label=""
                                page="policy-repository"
                                :search-query="searchQuery"
                                @execute-search="executeSearch"
                                @clear-form="clearSearchQuery"
                            />
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
                        <span class="loading__span">Loading...</span>
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
