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
                    <JumpTo />
                </template>
                <template #links>
                    <HeaderLinks
                        :about-url="aboutUrl"
                        :resources-url="resourcesUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch
                        :search-url="searchUrl"
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
                        <RegResults
                            :base="base"
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
                        <ResourcesResults
                            :base="base"
                            :count="resourcesResults.length"
                            :parts-last-updated="partsLastUpdated"
                            :parts-list="partsList"
                            :results="filteredContent"
                            :query="searchQuery"
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
                        </ResourcesResults>
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

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import Banner from "@/components/Banner.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import RegResults from "@/components/reg_search/RegResults.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SearchInput from "@/components/SearchInput.vue";

import { getCurrentPageResultsRange, stripQuotes } from "@/utilities/utils";
import {
    getFormattedPartsList,
    getLastUpdatedDates,
    getRegSearchResults,
    getSupplementalContent,
    getSynonyms,
} from "@/utilities/api";

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
        RegResults,
        ResourcesResults,
        SearchEmptyState,
        SearchInput,
    },

    props: {
        aboutUrl: {
            type: String,
            default: "/about/",
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
        }
    },

    beforeCreate() {},

    async created() {
        if (this.searchQuery) {
            await Promise.allSettled([
                this.getPartLastUpdatedDates(),
                getFormattedPartsList(),
            ]).then((data) => {
                // eslint-disable-next-line
                this.partsList = data[1].value;
            });

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
            base:
                import.meta.env.VITE_ENV && import.meta.env.VITE_ENV !== "prod"
                    ? `/${import.meta.env.VITE_ENV}`
                    : "",
            pageSize: 50,
            regsLoading: true,
            resourcesLoading: true,
            partsLastUpdated: {},
            partsList: [],
            queryParams: this.$route.query,
            regResults: [],
            totalRegResultsCount: 0,
            resourcesResults: [],
            totalResourcesResultsCount: 0,
            searchInputValue: undefined,
            synonyms: [],
            unquotedSearch: false,
        };
    },

    computed: {
        isLoading() {
            return this.regsLoading || this.resourcesLoading;
        },
        filteredContent() {
            return this.resourcesResults.map((item) => {
                const copiedItem = JSON.parse(JSON.stringify(item));
                copiedItem.locations = item.locations.filter(
                    (location) => this.partsLastUpdated[location.part]
                );
                return copiedItem;
            });
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
            try {
                const response = await getSupplementalContent({
                    partDict: "all",
                    q: query,
                    page,
                    page_size: pageSize,
                    fr_grouping: false,
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
        async getPartLastUpdatedDates() {
            this.partsLastUpdated = await getLastUpdatedDates(this.apiUrl);
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

<style lang="scss">
#searchApp.search-view {
    display: flex;
    flex-direction: column;

    > .nav-container {
        padding: 0 90px;
    }

    .search-form {
        margin-bottom: 30px;
    }

    .combined-results-container {
        overflow: auto;
        margin-bottom: 16px;
        padding: 0 45px;
        display: flex;
        justify-content: space-between;

        @mixin common-results-styles {
            flex: 1;
            margin: 0 auto;
            padding: 0 45px;
            @content;
        }

        .reg-results-content {
            @include common-results-styles {
                .result {
                    margin-top: 0px;
                }
            }
        }

        .resources-results-content {
            @include common-results-styles;

            .result-content-wrapper {
                margin-bottom: 0px;

                .supplemental-content {
                    margin-bottom: 5px;

                    a.supplemental-content-link {
                        .supplemental-content-date,
                        .supplemental-content-title,
                        .supplemental-content-description {
                            font-size: $font-size-md;
                            line-height: 22px;
                        }
                    }
                }
            }

            .related-sections {
                margin-bottom: 25px;
                font-size: $font-size-xs;
                color: $mid_gray;

                .related-sections-title {
                    text-transform: uppercase;
                    font-weight: 600;
                    color: $dark_gray;
                }

                .related-section-link {
                    font-size: $font-size-sm;
                }

                a {
                    text-decoration: none;
                }
            }
        }

        .search-results-count {
            h2 {
                border-bottom: 2px solid $mid_blue;
                margin-block-end: 1em !important;
            }
        }
    }

    .pagination-expand-row {
        display: flex;
        flex-direction: row;
        justify-content: center;
        margin-bottom: 100px;

        .pagination-expand-container {
            width: 100%;
            max-width: 521px;
            margin: 0 45px;

            .pagination-expand-cta {
                margin-top: 14px;
            }
        }
    }
}
</style>
