<template>
    <body class="ds-base search-page">
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
                        :statutes-url="statutesUrl"
                        :subjects-url="subjectsUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
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
                        <RegResults :results="regResults" :query="searchQuery">
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
                        <PolicyResults
                            :base="homeUrl"
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
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import { getCurrentPageResultsRange, stripQuotes } from "utilities/utils";
import {
    getCombinedContent,
    getLastUpdatedDates,
    getRegSearchResults,
    getSupplementalContent,
    getSynonyms,
    getTitles,
} from "utilities/api";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import Banner from "@/components/Banner.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import PolicyResults from "@/components/subjects/PolicyResults.vue";
import RegResults from "@/components/search/RegResults.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SearchInput from "@/components/SearchInput.vue";

const DEFAULT_TITLE = "42";

export default {
    name: "SearchView",

    components: {
        Banner,
        BlockingModal,
        FlashBanner,
        HeaderComponent,
        HeaderLinks,
        HeaderSearch,
        IFrameContainer,
        JumpTo,
        PaginationController,
        PolicyResults,
        RegResults,
        SearchEmptyState,
        SearchInput,
    },

    props: {
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
    },

    provide() {
        return {
            base: this.homeUrl,
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
            regResults: [],
            totalRegResultsCount: 0,
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
            try {
                const response = await getRegSearchResults({
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
                this.regResults = [];
                this.totalRegResultsCount = 0;
            }
        },
        async retrieveResourcesResults({ query, page, pageSize }) {
            const requestParams = `q=${query}&page=${
                page ?? 1
            }&page_size=${pageSize}&paginate=true`;
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

            this.regsLoading = true;
            this.resourcesLoading = true;

            this.retrieveResourcesResults({ query, page, pageSize }).then(
                () => {
                    this.resourcesLoading = false;
                }
            );

            this.retrieveRegResults({ query, page, pageSize }).then(() => {
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
