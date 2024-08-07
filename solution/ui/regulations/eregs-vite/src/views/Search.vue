<template>
    <body class="ds-base search-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :home-url="homeUrl" />
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
        <div id="searchApp" class="search-view">
            <Banner title="Search Results">
                <template #input>
                    <SearchInput
                        form-class="search-form"
                        label="Search Regulations"
                        page="search"
                        :search-query="searchQuery"
                        :synonyms="synonyms"
                        @execute-search="executeSearch"
                        @clear-form="clearSearchQuery"
                    />
                </template>
            </Banner>
            <div class="combined-results-container">
                <div class="reg-results-content">
                    <div class="search-results-count">
                        <h2>Regulations</h2>
                        <span v-if="regsLoading">Loading...</span>
                        <span
                            v-else-if="regsError"
                            class="regs-count__span--error"
                            >We're unable to display results for this query
                            right now</span
                        >
                        <span v-else>
                            <span v-if="totalRegResultsCount > 0">
                                {{ currentPageRegResultsRange[0] }} -
                                {{ currentPageRegResultsRange[1] }} of
                            </span>
                            {{ totalRegResultsCount }} result<span
                                v-if="totalRegResultsCount != 1"
                                >s</span
                            >
                        </span>
                    </div>
                    <template v-if="!regsLoading">
                        <template v-if="regsError">
                            <SearchErrorMsg :survey-url="surveyUrl" />
                            <template
                                v-if="!isLoading && resourcesResults.length > 0"
                            >
                                <SearchEmptyState
                                    :query="searchQuery"
                                    :show-internal-link="false"
                                />
                            </template>
                        </template>
                        <RegResults
                            v-else
                            :results="regResults"
                            :query="searchQuery"
                        >
                            <template #empty-state>
                                <template
                                    v-if="
                                        regResults.length == 0 &&
                                        combinedPageCount > 0 &&
                                        !isLoading
                                    "
                                >
                                    <SearchEmptyState
                                        :query="searchQuery"
                                        :show-internal-link="false"
                                    />
                                </template>
                            </template>
                        </RegResults>
                    </template>
                </div>
                <div class="resources-results-content">
                    <div class="search-results-count">
                        <h2>Resources</h2>
                        <span v-if="resourcesLoading">Loading...</span>
                        <span
                            v-else-if="resourcesError"
                            class="resources-count__span--error"
                            >We're unable to display results for this query
                            right now</span
                        >
                        <span v-else>
                            <span v-if="totalResourcesResultsCount > 0">
                                {{ currentPageResourcesResultsRange[0] }} -
                                {{ currentPageResourcesResultsRange[1] }} of
                            </span>
                            {{ totalResourcesResultsCount }} result<span
                                v-if="totalResourcesResultsCount != 1"
                                >s</span
                            >
                        </span>
                    </div>
                    <template v-if="!resourcesLoading">
                        <template v-if="resourcesError">
                            <SearchErrorMsg :survey-url="surveyUrl" />
                            <template
                                v-if="!isLoading && regResults.length > 0"
                            >
                                <SearchEmptyState
                                    :query="searchQuery"
                                    :show-internal-link="false"
                                />
                            </template>
                        </template>
                        <PolicyResults
                            v-else
                            :base="homeUrl"
                            :categories="combinedCategories.data ?? []"
                            :parts-last-updated="partsLastUpdated"
                            :results="resourcesResults"
                            view="search"
                        >
                            <template #empty-state>
                                <template
                                    v-if="
                                        resourcesResults.length == 0 &&
                                        combinedPageCount > 0 &&
                                        !isLoading
                                    "
                                >
                                    <SearchEmptyState
                                        :query="searchQuery"
                                        :show-internal-link="false"
                                    />
                                </template>
                            </template>
                        </PolicyResults>
                    </template>
                </div>
            </div>
            <div v-if="!isLoading" class="pagination-expand-row">
                <div class="pagination-expand-container">
                    <PaginationController
                        v-if="totalCount > 0"
                        :count="paginationCount"
                        :page="page"
                        :page-size="pageSize"
                        view="search"
                    />
                    <div
                        v-if="
                            (regResults.length > 0 &&
                                resourcesResults.length > 0) ||
                            totalCount == 0
                        "
                        class="pagination-expand-cta"
                    >
                        <SearchEmptyState
                            :query="searchQuery"
                            :show-internal-link="false"
                        />
                    </div>
                </div>
            </div>
        </div>
    </body>
</template>

<script>
import { useRoute, useRouter } from "vue-router";
import useCategories from "composables/categories";

import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import { getCurrentPageResultsRange, stripQuotes } from "utilities/utils";
import {
    getCombinedContent,
    getLastUpdatedDates,
    getRegSearchResults,
    getSynonyms,
    getTitles,
} from "utilities/api";

import Banner from "@/components/Banner.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import SignInLink from "@/components/SignInLink.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import PolicyResults from "@/components/subjects/PolicyResults.vue";
import RegResults from "@/components/search/RegResults.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SearchErrorMsg from "@/components/SearchErrorMsg.vue";
import SearchInput from "@/components/SearchInput.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";

const DEFAULT_TITLE = "42";

export default {
    name: "SearchView",

    components: {
        Banner,
        HeaderComponent,
        HeaderLinks,
        HeaderSearch,
        SignInLink,
        JumpTo,
        PaginationController,
        PolicyResults,
        RegResults,
        SearchEmptyState,
        SearchErrorMsg,
        SearchInput,
        HeaderUserWidget,
    },

    props: {
        adminUrl: {
            type: String,
            default: "/admin/",
        },
        aboutUrl: {
            type: String,
            default: "/about/",
        },
        apiUrl: {
            type: String,
            default: "/v3/",
        },
        customLoginUrl: {
            type: String,
            default: "/login",
        },
        homeUrl: {
            type: String,
            default: "/",
        },
        isAuthenticated: {
            type: Boolean,
            default: false,
        },
        searchUrl: {
            type: String,
            default: "/search/",
        },
        statutesUrl: {
            type: String,
            default: "/statutes/",
        },
        subjectsUrl: {
            type: String,
            default: "/subjects/",
        },
        surveyUrl: {
            type: String,
            default: "",
        },
        username: {
            type: String,
            default: undefined,
        },
    },

    setup(props) {
        const $route = useRoute();
        const $router = useRouter();

        const combinedCategories = useCategories({
            apiUrl: props.apiUrl,
            isAuthenticated: props.isAuthenticated,
        });

        return { $route, $router, combinedCategories };
    },

    provide() {
        return {
            apiUrl: this.apiUrl,
            base: this.homeUrl,
            currentRouteName: this.$route.name,
        };
    },

    beforeCreate() {},

    async created() {
        if (this.searchQuery) {
            this.titles = await getTitles();
            this.partsLastUpdated = await getLastUpdatedDates(
                this.apiUrl,
                this.titles
            );
            this.retrieveSynonyms(this.searchQuery);
            this.retrieveAllResults({
                query: this.searchQuery,
                page: this.page,
                pageSize: this.pageSize,
            });
        } else {
            this.regsLoading = false;
            this.resourcesLoading = false;
        }
    },

    data() {
        return {
            pageSize: 50,
            regsLoading: true,
            resourcesLoading: true,
            partsLastUpdated: {},
            queryParams: this.$route.query,
            regsError: false,
            regResults: [],
            totalRegResultsCount: 0,
            resourcesError: false,
            resourcesResults: [],
            totalResourcesResultsCount: 0,
            searchInputValue: undefined,
            synonyms: [],
            unquotedSearch: false,
            titles: [DEFAULT_TITLE],
        };
    },

    computed: {
        isLoading() {
            return this.regsLoading || this.resourcesLoading;
        },
        page() {
            return _isUndefined(this.queryParams.page)
                ? this.queryParams.page
                : parseInt(this.queryParams.page, 10);
        },
        searchQuery: {
            get() {
                return this.queryParams.q || undefined;
            },
            set(value) {
                this.searchInputValue = value;
            },
        },
        multiWordQuery() {
            if (this.searchQuery === undefined) return false;

            return (
                this.searchQuery.split(" ").length > 1 &&
                this.searchQuery[0] !== '"' &&
                this.searchQuery[this.searchQuery.length - 1] !== '"'
            );
        },
        combinedPageCount() {
            return this.regResults.length + this.resourcesResults.length;
        },
        paginationCount() {
            return Math.max(
                this.totalRegResultsCount,
                this.totalResourcesResultsCount
            );
        },
        totalCount() {
            return this.totalRegResultsCount + this.totalResourcesResultsCount;
        },
        currentPageRegResultsRange() {
            return getCurrentPageResultsRange({
                count: this.totalRegResultsCount,
                page: this.page,
                pageSize: this.pageSize,
            });
        },
        currentPageResourcesResultsRange() {
            return getCurrentPageResultsRange({
                count: this.totalResourcesResultsCount,
                page: this.page,
                pageSize: this.pageSize,
            });
        },
    },

    methods: {
        removeQuotes(string) {
            return stripQuotes(string);
        },
        setTitle(query) {
            const querySubString = query ? `for ${query} ` : "";
            document.title = `Search ${querySubString}| Medicaid & CHIP eRegulations`;
        },
        async retrieveRegResults({ query, page, pageSize }) {
            this.regsError = false;
            try {
                const response = await getRegSearchResults({
                    apiUrl: this.apiUrl,
                    q: query,
                    page,
                    page_size: pageSize,
                });
                this.regResults = response?.results ?? [];
                this.totalRegResultsCount = response?.count ?? 0;
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.regsError = true;
                this.regResults = [];
                this.totalRegResultsCount = 0;
            }
        },
        async retrieveResourcesResults({ query, page, pageSize }) {
            this.resourcesError = false;
            const requestParams = `q=${query}&page=${
                page ?? 1
            }&page_size=${pageSize}`;
            let response = "";
            try {
                response = await getCombinedContent({
                    apiUrl: this.apiUrl,
                    cacheResponse: false,
                    requestParams,
                });

                this.resourcesResults = response?.results ?? [];
                this.totalResourcesResultsCount = response?.count ?? 0;
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.resourcesError = true;
                this.resourcesResults = [];
                this.totalResourcesResultsCount = 0;
            }
        },
        async retrieveAllResults({ query, page, pageSize }) {
            if (!query) {
                this.regResults = [];
                this.resourcesResults = [];

                return;
            }

            const encodedQuery = encodeURIComponent(query);

            this.regsLoading = true;
            this.resourcesLoading = true;

            this.retrieveResourcesResults({
                query: encodedQuery,
                page,
                pageSize,
            }).then(() => {
                this.resourcesLoading = false;
            });

            this.retrieveRegResults({
                query,
                page,
                pageSize,
            }).then(() => {
                this.regsLoading = false;
            });
        },
        async retrieveSynonyms(query) {
            this.synonyms = [];

            if (!query) {
                return;
            }

            try {
                const synonyms = await getSynonyms(this.removeQuotes(query));

                const activeSynonyms = synonyms.map((word) =>
                    word.synonyms
                        .filter((synonym) => synonym.isActive === true)
                        .map((synonym) => synonym.baseWord)
                )[0];

                this.synonyms = activeSynonyms ?? [];
            } catch (error) {
                console.error("Error retrieving synonyms");
                this.synonyms = [];
            }
        },
        executeSearch(payload) {
            this.synonyms = [];
            this.$router.push({
                name: "search",
                query: {
                    q: payload.query,
                },
            });
        },
        clearSearchQuery() {
            this.synonyms = [];
            this.totalRegResultsCount = 0;
            this.totalResourcesResultsCount = 0;
            this.$router.push({
                name: "search",
                query: {
                    page: undefined,
                    q: undefined,
                },
            });
        },
    },

    watch: {
        "$route.query": {
            async handler(toQueries) {
                this.queryParams = toQueries;
            },
        },
        queryParams: {
            async handler(newParams, oldParams) {
                const queryChanged = newParams.q !== oldParams.q;
                const pageChanged = newParams.page !== oldParams.page;

                if (queryChanged) {
                    this.setTitle(this.searchQuery);

                    if (_isEmpty(this.searchQuery)) {
                        this.regResults = [];
                        this.resourcesResults = [];
                        return;
                    }

                    this.retrieveSynonyms(this.searchQuery);
                }

                if (queryChanged || pageChanged) {
                    this.retrieveAllResults({
                        query: this.searchQuery,
                        page: this.page,
                        pageSize: this.pageSize,
                    });
                }
            },
        },
    },
};
</script>
