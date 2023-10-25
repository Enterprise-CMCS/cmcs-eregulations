<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router/composables";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";

import {
    getCombinedContent,
    getLastUpdatedDates,
    getPolicyDocSubjects,
    getTitles,
} from "utilities/api";

import { getSubjectName, sortSubjects } from "utilities/filters";

import { getRequestParams, PARAM_VALIDATION_DICT } from "utilities/utils";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import DocumentTypeSelector from "@/components/policy-repository/DocumentTypeSelector.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import PolicyResults from "@/components/policy-repository/PolicyResults.vue";
import PolicySelections from "@/components/policy-repository/PolicySelections.vue";
import PolicySidebar from "@/components/policy-repository/PolicySidebar.vue";
import SearchInput from "@/components/SearchInput.vue";
import SubjectSelector from "@/components/policy-repository/SubjectSelector.vue";
import SubjectTOC from "@/components/policy-repository/SubjectTOC.vue";

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
    type: "Type",
    q: "query",
};

// provide Django template variables
provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);
provide("FilterTypesDict", FilterTypesDict);

// search query refs and methods
const searchQuery = ref($route.query.q || "");
const clearSearchQuery = () => {
    searchQuery.value = "";
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

const clearSearchInput = () => {
    const { q, page, ...rest } = $route.query;
    $router.push({
        name: "policy-repository",
        query: {
            ...rest,
        },
    });
};

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
        const contentList = await getCombinedContent({
            apiUrl: props.apiUrl,
            cacheResponse: !props.isAuthenticated,
            requestParams,
        });
        policyDocList.value.results = contentList.results;
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

const clearSelectedParams = () => {
    selectedParams.paramString = "";
    selectedParams.paramsArray = [];
};

provide("selectedParams", selectedParams);

const setSelectedParams = (subjectsListRef) => (param) => {
    const [paramType, paramValue] = param;

    if (paramType === "q") {
        searchQuery.value = paramValue;
        return;
    }

    const paramList = !_isArray(paramValue) ? [paramValue] : paramValue;
    paramList.forEach((paramId) => {
        const subject = subjectsListRef.value.results.filter(
            (subjectObj) => paramId === subjectObj.id.toString()
        )[0];

        if (subject) {
            addSelectedParams({
                type: paramType,
                id: paramId,
                name: getSubjectName(subject),
            });
        }
    });
};

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
            // wipe everything clean to start
            clearSelectedParams();
            clearSearchQuery();

            // now that everything is cleaned, iterate over new query params
            Object.entries($route.query).forEach((param) => {
                setSelectedParams(policyDocSubjects)(param);
            });

            getDocList(getRequestParams($route.query));
        }
    }
};

/**
* @param {Object} queryParams - $route.query
* @returns {Boolean} - true if all doc types are selected and nothing else
*/
const allDocTypesOnly = (queryParams) => {
    if (
        queryParams.type &&
        ((queryParams.type.includes("internal") &&
            queryParams.type.includes("external")) ||
            queryParams.type.includes("all"))
    ) {
        const { type, ...rest } = queryParams;
        return _isEmpty(rest);
    }

    return false;
};

watch(
    () => $route.query,
    async (newQueryParams) => {
        // wipe everything clean to start
        clearSelectedParams();
        clearSearchQuery();

        const sanitizedQueryParams = Object.entries(newQueryParams).filter(
            ([key]) => PARAM_VALIDATION_DICT[key]
        );

        // if all params are removed, return
        if (_isEmpty(sanitizedQueryParams)) {
            return;
        }

        // if both internal and external checkboxes are selected and nothing else, return
        if (allDocTypesOnly($route.query)) {
            return;
        }

        // now that everything is cleaned, iterate over new query params
        Object.entries(newQueryParams).forEach(
            setSelectedParams(policyDocSubjects)
        );

        // parse $route.query to return `${key}=${value}` string
        // and provide to getDocList
        const newRequestParams = getRequestParams(newQueryParams);
        await getDocList(newRequestParams);
    }
);

// fetches on page load
getPartsLastUpdated();
getDocSubjects();
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
                                label="Search for a document"
                                page="policy-repository"
                                :search-query="searchQuery"
                                @execute-search="executeSearch"
                                @clear-form="clearSearchInput"
                            />
                        </template>
                        <template #filters>
                            <DocumentTypeSelector />
                            <SubjectSelector
                                :policy-doc-subjects="policyDocSubjects"
                            />
                        </template>
                    </PolicySidebar>
                </div>
                <div class="ds-l-col--12 ds-l-md-col--8 ds-l-lg-col--9">
                    <SubjectTOC
                        v-if="
                            allDocTypesOnly($route.query) ||
                            _isEmpty($route.query)
                        "
                        :policy-doc-subjects="policyDocSubjects"
                    />
                    <template
                        v-else-if="
                            policyDocList.loading || partsLastUpdated.loading
                        "
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
