<script setup>
import { inject, provide, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import useSearchResults from "composables/searchResults";
import useRemoveList from "composables/removeList";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";

import {
    getLastUpdatedDates,
    getInternalSubjects,
    getTitles,
} from "utilities/api";

import { getSubjectName } from "utilities/filters";

import { getRequestParams, PARAM_VALIDATION_DICT } from "utilities/utils";

import CategoriesDropdown from "@/components/dropdowns/Categories.vue";
import DocumentTypeSelector from "@/components/subjects/DocumentTypeSelector.vue";
import FetchCategoriesContainer from "@/components/dropdowns/fetchCategoriesContainer.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import PolicyResults from "@/components/subjects/PolicyResults.vue";
import SearchErrorMsg from "@/components/SearchErrorMsg.vue";
import SearchInput from "@/components/SearchInput.vue";
import SignInLink from "@/components/SignInLink.vue";

const adminUrl = inject("adminUrl");
const apiUrl = inject("apiUrl");
const customLoginUrl = inject("customLoginUrl");
const hasEditableJobCode = inject("hasEditableJobCode");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");
const searchUrl = inject("searchUrl");
const statutesUrl = inject("statutesUrl");
const subjectsUrl = inject("subjectsUrl");
const surveyUrl = inject("surveyUrl");
const username = inject("username");

// Router and Route
const $route = useRoute();
const $router = useRouter();

const pageSize = 50;

// show/hide categories dropdown
const showCategoriesRef = ref();

const setShowCategories = (type) => {
    // hide categories dropdown if only regulations are selected
    if (
        type &&
        type.split(",").length === 1 &&
        type.split(",")[0] === "regulations"
    ) {
        showCategoriesRef.value = false;
    } else {
        showCategoriesRef.value = true;
    }
};

setShowCategories($route.query.type);

// provide Django template variables
provide("currentRouteName", $route.name);

// provide router query params to remove on child component change
const commonRemoveList = ["page", "categories", "intcategories"];
const searchInputRemoveList = commonRemoveList.concat(["q"]);

provide("commonRemoveList", commonRemoveList);

const categoriesRef = ref([]);
const setCategories = (categories) => {
    categoriesRef.value = categories;
};

/**
 * @param {Object} queryParams - $route.query
 * @returns {Boolean} - true if all doc types are selected and nothing else
 */
const allDocTypesOnly = (queryParams) => {
    const { type, ...rest } = queryParams;
    if (
        (type && type.includes("all") && _isEmpty(rest)) ||
        (!type && _isEmpty(rest))
    ) {
        return true;
    }

    return false;
};

// search query refs and methods
const searchQuery = ref($route.query.q || "");
const clearSearchQuery = () => {
    searchQuery.value = "";
};

const executeSearch = (payload) => {
    const routeClone = { ...$route.query };

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList: searchInputRemoveList,
    });

    $router.push({
        name: "search",
        query: {
            ...cleanedRoute,
            q: payload.query,
        },
    });
};

const resetSearch = () => {
    $router.push({
        name: "search",
        query: {},
    });
};

// partsLastUpdated fetch for related regulations citations filtering
const partsLastUpdated = ref({
    results: {},
    loading: true,
});

const getPartsLastUpdated = async () => {
    try {
        const titles = await getTitles({ apiUrl });
        partsLastUpdated.value.results = await getLastUpdatedDates({
            apiUrl,
            titles,
        });
    } catch (error) {
        console.error(error);
    } finally {
        partsLastUpdated.value.loading = false;
    }
};

const { policyDocList, getDocList, clearDocList } = useSearchResults();

// use "reactive" method to make urlParams reactive when provided/injected
// selectedParams.paramString is used as the reactive prop
const selectedParams = reactive({
    paramString: "",
    paramsArray: [],
});

// method to add selected params
const addSelectedParams = (paramArgs) => {
    const { id, name, type } = paramArgs;

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

    if (commonRemoveList.includes(paramType)) {
        return;
    }

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

const setTitle = (query) => {
    const querySubString = query ? `for ${query} ` : "";
    document.title = `Search ${querySubString}| Medicaid & CHIP eRegulations`;
};

// called on load
const getDocSubjects = async () => {
    try {
        const subjectsResponse = await getInternalSubjects({
            apiUrl,
        });

        policyDocSubjects.value.results = subjectsResponse.results;
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;

        if (!$route.query.q) {
            clearDocList();
            return;
        }

        // wipe everything clean to start
        clearSelectedParams();
        clearSearchQuery();

        // now that everything is cleaned, iterate over new query params
        Object.entries($route.query).forEach((param) => {
            setSelectedParams(policyDocSubjects)(param);
        });

        getDocList({
            apiUrl,
            pageSize,
            requestParamString: getRequestParams($route.query),
            query: $route.query.q,
            type: $route.query.type,
        });
    }
};

watch(
    () => $route.query,
    async (newQueryParams) => {
        const { q, type } = newQueryParams;

        setShowCategories(type);

        // wipe everything clean to start
        clearSelectedParams();
        clearSearchQuery();

        // set document title
        setTitle(q);

        // early return if there's no query
        if (!q) {
            clearDocList();
            return;
        }

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
        getDocList({
            apiUrl,
            pageSize,
            requestParamString: newRequestParams,
            query: $route.query.q,
            type: $route.query.type,
        });
    }
);

// fetches on page load
getPartsLastUpdated();
getDocSubjects();
</script>

<template>
    <body class="ds-base search-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :apiUrl="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :statutes-url="statutesUrl"
                        :subjects-url="subjectsUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
                <template v-if="isAuthenticated" #sign-in>
                    <HeaderUserWidget :admin-url="adminUrl">
                        <template #username>
                            {{ username }}
                        </template>
                    </HeaderUserWidget>
                </template>
                <template v-else #sign-in>
                    <SignInLink
                        :custom-login-url="customLoginUrl"
                        :home-url="homeUrl"
                        :is-authenticated="isAuthenticated"
                        :route="$route"
                    />
                </template>
            </HeaderComponent>
        </header>
        <main id="searchApp" class="search-view">
            <h1>Search Results</h1>
            <section class="query-filters__section" role="search">
                <SearchInput
                    form-class="search-form"
                    label="Search for a document"
                    parent="search"
                    :search-query="searchQuery"
                    @execute-search="executeSearch"
                    @clear-form="resetSearch"
                />
                <fieldset class="search__fieldset" v-if="$route.query.q">
                    <DocumentTypeSelector parent="search" />
                    <FetchCategoriesContainer
                        v-slot="slotProps"
                        :categories-capture-function="setCategories"
                    >
                        <CategoriesDropdown
                            v-show="showCategoriesRef"
                            :list="slotProps.data"
                            :error="slotProps.error"
                            :loading="
                                slotProps.loading || policyDocList.loading
                            "
                            parent="search"
                        />
                    </FetchCategoriesContainer>
                </fieldset>
            </section>
            <section class="search-results">
                <template
                    v-if="policyDocList.loading || partsLastUpdated.loading"
                >
                    <span class="loading__span">Loading...</span>
                </template>
                <template v-else-if="policyDocList.error">
                    <div class="doc__list">
                        <SearchErrorMsg
                            :search-query="searchQuery"
                            show-apology
                            :survey-url="surveyUrl"
                        />
                    </div>
                </template>
                <template v-else-if="policyDocList.results === 0">
                    <div class="doc__list">No results</div>
                </template>
                <template v-else>
                    <PolicyResults
                        :categories="categoriesRef"
                        :results="policyDocList.results"
                        :results-count="policyDocList.count"
                        :page="parseInt($route.query.page, 10) || 1"
                        :page-size="pageSize"
                        :parts-last-updated="partsLastUpdated.results"
                        :has-editable-job-code="hasEditableJobCode"
                        :search-query="searchQuery"
                        :selected-subject-parts="selectedSubjectParts"
                        view="search"
                    />
                    <div class="pagination-expand-row">
                        <div class="pagination-expand-container">
                            <PaginationController
                                v-if="policyDocList.count > 0"
                                :count="policyDocList.count"
                                :page="parseInt($route.query.page, 10) || 1"
                                :page-size="pageSize"
                                view="search"
                            />
                        </div>
                    </div>
                </template>
            </section>
        </main>
    </body>
</template>
