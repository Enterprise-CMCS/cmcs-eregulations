<template>
    <body class="ds-base search-page">
        <BlockingModal where-used="vite">
            <IFrameContainer
                src="https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
                title="Google Forms iframe"
            />
        </BlockingModal>
        <FlashBanner where-used="vite" />
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
                        <span v-else>{{ regResults.length }} results</span>
                    </div>
                    <template v-if="!regsLoading">
                        <RegResults :base="base" :results="regResults">
                            <template #empty-state>
                                <template
                                    v-if="
                                        regResults.length == 0 &&
                                        totalResultsCount > 0 &&
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
                        <span v-else
                            >{{ resourcesResults.length }} results</span
                        >
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
                                        totalResultsCount > 0 &&
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
                    <template
                        v-if="
                            (regResults.length > 0 &&
                                resourcesResults.length > 0) ||
                            (regResults.length == 0 &&
                                resourcesResults.length == 0)
                        "
                    >
                        <SearchEmptyState
                            :query="searchQuery"
                            :show-internal-link="false"
                        />
                    </template>
                </div>
            </div>
        </div>
    </body>
</template>

<script>
import _isEmpty from "lodash/isEmpty";

import { stripQuotes } from "@/utilities/utils";
import {
    getFormattedPartsList,
    getLastUpdatedDates,
    getRegSearchResults,
    getSupplementalContentV3,
    getSynonyms,
} from "@/utilities/api";

import Banner from "@/components/Banner.vue";
import BlockingModal from "legacy/js/src/components/BlockingModal.vue";
import FlashBanner from "legacy/js/src/components/FlashBanner.vue";
import IFrameContainer from "legacy/js/src/components/IFrameContainer.vue";
import RegResults from "@/components/reg_search/RegResults.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SearchInput from "@/components/SearchInput.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
        BlockingModal,
        FlashBanner,
        IFrameContainer,
        RegResults,
        ResourcesResults,
        SearchEmptyState,
        SearchInput,
    },

    props: {},

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
            this.retrieveAllResults(this.searchQuery);
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
            regsLoading: true,
            resourcesLoading: true,
            partsLastUpdated: {},
            partsList: [],
            queryParams: this.$route.query,
            regResults: [],
            resourcesResults: [],
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
        totalResultsCount() {
            return this.regResults.length + this.resourcesResults.length;
        },
        regCountLabel() {
            return this.totalResultsCount > 0
                ? "results"
                : "results in Regulations or Resources";
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
        async retrieveRegResults(query) {
            try {
                const response = await getRegSearchResults(query);
                this.regResults = response?.results ?? [];
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.regResults = [];
            }
        },
        async retrieveResourcesResults(query) {
            try {
                const response = await getSupplementalContentV3({
                    partDict: "all",
                    q: query,
                    fr_grouping: false,
                });
                this.resourcesResults = response?.results ?? [];
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.resourcesResults = [];
            }
        },
        async retrieveAllResults(query) {
            if (!query) {
                this.regResults = [];
                this.resourcesResults = [];

                return;
            }

            this.regsLoading = true;
            this.resourcesLoading = true;

            this.retrieveResourcesResults(query).then(() => {
                this.resourcesLoading = false;
            });

            this.retrieveRegResults(query).then(() => {
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
            this.$router.push({
                name: "search",
                query: {
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
            // beware, some yucky code ahead...
            async handler(newParams, oldParams) {
                if (newParams.q !== oldParams.q) {
                    this.setTitle(this.searchQuery);

                    if (_isEmpty(this.searchQuery)) {
                        this.regResults = [];
                        this.resourcesResults = [];
                        return;
                    }

                    this.retrieveSynonyms(this.searchQuery);
                    this.retrieveAllResults(this.searchQuery);
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
        margin-bottom: 30px;
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
            }
        }
    }

    .pagination-expand-row {
        display: flex;
        flex-direction: row;
        justify-content: center;
        margin-bottom: 100px;
    }
}
</style>
