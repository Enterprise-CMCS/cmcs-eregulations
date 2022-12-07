<template>
    <body class="ds-base search-page">
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
                        <span v-if="isLoading">Loading...</span>
                        <span v-else
                            >{{ regResults.length }} results in Medicaid & CHIP
                            Regulations</span
                        >
                    </div>
                    <template v-if="!isLoading">
                        <RegResults
                            :base="base"
                            :results="regResults"
                            :search-query="searchQuery"
                        />
                    </template>
                </div>
                <div class="resources-results-content">
                    <template v-if="!isLoading">
                        <ResourcesResults
                            :base="base"
                            :count="resourcesResults.length"
                            :parts-last-updated="partsLastUpdated"
                            :parts-list="partsList"
                            :results="resourcesResults"
                            :search-query="searchQuery"
                            view="search"
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
import RegResults from "@/components/reg_search/RegResults.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";
import SearchInput from "@/components/SearchInput.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
        RegResults,
        ResourcesResults,
        SearchInput,
    },

    props: {},

    beforeCreate() {},

    async created() {
        // promise.all these
        await this.getPartLastUpdatedDates();
        await getFormattedPartsList();

        if (this.searchQuery) {
            this.retrieveSynonyms(this.searchQuery);

            // we need to Promise.all() these
            this.retrieveResourcesResults(this.searchQuery);
            this.retrieveRegResults(this.searchQuery);
        }
    },

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            base:
                import.meta.env.VITE_ENV && import.meta.env.VITE_ENV !== "prod"
                    ? `/${import.meta.env.VITE_ENV}`
                    : "",
            isLoading: false,
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
    },

    methods: {
        removeQuotes(string) {
            return stripQuotes(string);
        },
        async retrieveRegResults(query) {
            this.isLoading = true;

            if (!query) {
                this.isLoading = false;
                this.regResults = [];
            }

            try {
                const response = await getRegSearchResults(query);
                this.regResults = response?.results ?? [];
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.regResults = [];
            } finally {
                this.isLoading = false;
            }
        },
        async retrieveResourcesResults(query) {
            console.log("retrieving resources results");

            if (!query) {
                this.resourcesResults = [];
            }

            try {
                const response = await getSupplementalContentV3({
                    partDict: "all",
                    q: query,
                });
                console.log("response.results", response.results);
                this.resourcesResults = response?.results ?? [];
            } catch (error) {
                console.error(
                    "Error retrieving regulation search results: ",
                    error
                );
                this.resourcesResults = [];
            } finally {
                console.log("Resources request finished");
            }
        },
        async retrieveSynonyms(query) {
            if (!query) {
                this.synonyms = [];
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
                    if (_isEmpty(this.searchQuery)) {
                        this.regResults = [];
                        this.resourcesResults = [];
                        return;
                    }

                    this.retrieveRegResults(this.searchQuery);
                    this.retrieveResourcesResults(this.searchQuery);
                    this.retrieveSynonyms(this.searchQuery);
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

    .search-form {
        margin-bottom: 30px;
    }

    .combined-results-container {
        overflow: auto;
        width: 100%;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;

        @mixin common-results-styles {
            flex: 1;
            margin: 0 auto;
            padding: 0 $spacer-5;
            @include screen-xl {
                padding: 0 $spacer-4;
            }
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
        }
    }
}
</style>
