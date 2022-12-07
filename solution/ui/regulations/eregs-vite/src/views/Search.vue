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
                        <template v-else>
                            <h2>Regulations</h2>
                            <span>{{ regResults.length }} results</span>
                        </template>
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
                    <div class="search-results-count">
                        <template v-if="!isLoading">
                            <h2>Resources</h2>
                            <span>{{ resourcesResults.length }} results</span>
                        </template>
                    </div>
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
        await Promise.allSettled([
            this.getPartLastUpdatedDates(),
            getFormattedPartsList(),
        ]).then((data) => {
            // eslint-disable-next-line
            this.partsList = data[1].value;
        });

        if (this.searchQuery) {
            this.retrieveSynonyms(this.searchQuery);
            this.retrieveAllResults(this.searchQuery);
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
            isLoading: true,
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

            this.isLoading = true;

            Promise.allSettled([
                this.retrieveResourcesResults(query),
                this.retrieveRegResults(query),
            ]).then(() => {
                this.isLoading = false;
            });
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

        .search-results-count {
            h2 {
                border-bottom: 2px solid $mid_blue;
            }
        }
    }
}
</style>
