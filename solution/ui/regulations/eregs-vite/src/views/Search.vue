<script setup>
import { computed, inject, provide, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import useSearchResults from "composables/searchResults.js";
import useRemoveList from "composables/removeList.js";

import isEmpty from "lodash/isEmpty";

import { getLastUpdatedDates, getTitles } from "utilities/api.js";

import { getRequestParams, PARAM_VALIDATION_DICT } from "utilities/utils.js";

import AccessLink from "@/components/AccessLink.vue";
import CategoriesDropdown from "@/components/dropdowns/Categories.vue";
import DocumentTypeSelector from "@/components/subjects/DocumentTypeSelector.vue";
import FetchItemsContainer from "@/components/dropdowns/FetchItemsContainer.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import PolicyResults from "@/components/subjects/PolicyResults.vue";
import SearchContinueResearch from "@/components/SearchContinueResearch.vue";
import SearchErrorMsg from "@/components/SearchErrorMsg.vue";
import SearchInput from "@/components/SearchInput.vue";
import SignInCTA from "@/components/SignInCTA.vue";
import SignInLink from "@/components/SignInLink.vue";
import SubjectsDropdown from "@/components/dropdowns/Subjects.vue";

const accessUrl = inject("accessUrl");
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
const showDropdownsRef = ref();

const setShowDropdowns = (type) => {
    // hide categories dropdown if only regulations are selected
    if (
        type &&
        type.split(",").length === 1 &&
        type.split(",")[0] === "regulations"
    ) {
        showDropdownsRef.value = false;
    } else {
        showDropdownsRef.value = true;
    }
};

setShowDropdowns($route.query.type);

// provide Django template variables
provide("currentRouteName", $route.name);

// provide router query params to remove on child component change
const commonRemoveList = ["page"];
const searchInputRemoveList = commonRemoveList.concat([
    "q",
    "subjects",
    "categories",
    "intcategories",
]);

provide("commonRemoveList", commonRemoveList);

provide("parent", "search");

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
        (type && type.includes("all") && isEmpty(rest)) ||
        (!type && isEmpty(rest))
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

const setSelectedParams = (param) => {
    const [paramType, paramValue] = param;

    if (commonRemoveList.includes(paramType)) {
        return;
    }

    if (paramType === "q") {
        searchQuery.value = paramValue;
        return;
    }
};

const setTitle = (query) => {
    const querySubString = query ? `for ${query} ` : "";
    document.title = `Search ${querySubString}| Policy Connector`;
};

const getDocsOnLoad = async () => {
    if (!$route.query.q) {
        clearDocList();
        return;
    }

    // wipe everything clean to start
    clearSearchQuery();

    // now that everything is cleaned, iterate over new query params
    Object.entries($route.query).forEach((param) => {
        setSelectedParams(param);
    });

    getDocList({
        apiUrl,
        pageSize,
        requestParamString: getRequestParams({ queryParams: $route.query }),
        query: $route.query.q,
        type: $route.query.type,
    });
};

const sanitizeQueryParams = (queryParams) =>
    Object.entries(queryParams).filter(([key]) => PARAM_VALIDATION_DICT[key]);

const sanitizedQueryParams = ref(sanitizeQueryParams($route.query));

const activeFilters = computed(() =>
    sanitizedQueryParams.value.filter(([key, _value]) => key !== "q")
);

const hasActiveFilters = computed(() => activeFilters.value.length > 0);

watch(
    () => $route.query,
    async (newQueryParams) => {
        const { q, type } = newQueryParams;

        setShowDropdowns(type);

        // wipe everything clean to start
        clearSearchQuery();

        // set document title
        setTitle(q);

        // early return if there's no query
        if (!q) {
            clearDocList();
            return;
        }

        sanitizedQueryParams.value = sanitizeQueryParams(newQueryParams);

        // if all params are removed, return
        if (isEmpty(sanitizedQueryParams.value)) {
            return;
        }

        // if all three checkboxes are selected and nothing else, return
        if (allDocTypesOnly($route.query)) {
            return;
        }

        // now that everything is cleaned, iterate over new query params
        Object.entries(newQueryParams).forEach(setSelectedParams);

        // parse $route.query to return `${key}=${value}` string
        // and provide to getDocList
        const newRequestParams = getRequestParams({
            queryParams: newQueryParams,
        });
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
getDocsOnLoad();
</script>

<template>
    <body class="ds-base search-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
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
                <template #get-access>
                    <AccessLink v-if="!isAuthenticated" :base="homeUrl" />
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
                <fieldset v-if="$route.query.q" class="search__fieldset">
                    <DocumentTypeSelector
                        parent="search"
                        :loading="
                            policyDocList.loading || partsLastUpdated.loading
                        "
                    />
                    <div
                        v-show="showDropdownsRef"
                        class="search__fieldset--dropdowns"
                    >
                        <FetchItemsContainer
                            v-slot="slotProps"
                            items-to-fetch="subjects"
                            include-counts
                        >
                            <SubjectsDropdown
                                :list="slotProps.data"
                                :counts="slotProps.counts"
                                :loading="
                                    slotProps.loading || policyDocList.loading
                                "
                                parent="search"
                            />
                        </FetchItemsContainer>
                        <FetchItemsContainer
                            v-slot="slotProps"
                            items-to-fetch="categories"
                            :items-capture-function="setCategories"
                        >
                            <CategoriesDropdown
                                :list="slotProps.data"
                                :error="slotProps.error"
                                :loading="
                                    slotProps.loading || policyDocList.loading
                                "
                                parent="search"
                            />
                        </FetchItemsContainer>
                    </div>
                </fieldset>
            </section>
            <section class="search-results">
                <template v-if="!searchQuery" />
                <template
                    v-else-if="
                        policyDocList.loading || partsLastUpdated.loading
                    "
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
                <template v-else-if="policyDocList.results.length == 0">
                    <div class="doc__list">
                        <SignInCTA
                            v-if="!isAuthenticated"
                            class="login-cta__div--search-no-results"
                            :access-url="accessUrl"
                            :is-authenticated="isAuthenticated"
                            test-id="loginSearchNoResults"
                        >
                            <template #sign-in-link>
                                <SignInLink
                                    :custom-login-url="customLoginUrl"
                                    :home-url="homeUrl"
                                    :is-authenticated="isAuthenticated"
                                    :route="$route"
                                />
                            </template>
                        </SignInCTA>
                        <span class="no-results__span">Your search for
                            <strong>{{ searchQuery }}</strong> did not match any
                            results
                            <span v-if="hasActiveFilters">with the selected filters</span><span v-else>on eRegulations</span>.</span>
                    </div>
                    <SearchContinueResearch
                        :query="searchQuery"
                        :results-count="policyDocList.count"
                        :active-filters="activeFilters"
                    />
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
                    >
                        <template #sign-in-cta>
                            <SignInCTA
                                v-if="!isAuthenticated"
                                class="login-cta__div--search-results"
                                :access-url="accessUrl"
                                :is-authenticated="isAuthenticated"
                                test-id="loginSearchResults"
                            >
                                <template #sign-in-link>
                                    <SignInLink
                                        :custom-login-url="customLoginUrl"
                                        :home-url="homeUrl"
                                        :is-authenticated="isAuthenticated"
                                        :route="$route"
                                    />
                                </template>
                            </SignInCTA>
                        </template>
                    </PolicyResults>
                    <div class="pagination-expand-row">
                        <div class="pagination-expand-container">
                            <PaginationController
                                v-if="policyDocList.count > 0"
                                :count="policyDocList.count"
                                :page="parseInt($route.query.page, 10) || 1"
                                :page-size="pageSize"
                            />
                        </div>
                    </div>
                    <SearchContinueResearch
                        :query="searchQuery"
                        :results-count="policyDocList.count"
                        :active-filters="activeFilters"
                    />
                </template>
            </section>
        </main>
    </body>
</template>
