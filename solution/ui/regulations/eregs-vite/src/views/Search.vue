<template>
    <body class="ds-base search-page">
        <div id="searchApp" class="search-view">
            <Banner title="Search Results">
                <template #description>
                    <p>This site searches Title 42, Parts 400 and 430-460</p>
                </template>
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
            <div class="results-container">
                <div class="results-content">
                    <div class="search-results-count">
                        <span v-if="isLoading">Loading...</span>
                        <span v-else
                            >{{ results.length }} results in Medicaid & CHIP
                            Regulations</span
                        >
                    </div>
                    <template v-if="!isLoading">
                        <RegResults
                            :base="base"
                            :results="results"
                            :search-query="searchQuery"
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
import { getRegSearchResults, getSynonyms } from "@/utilities/api";

import Banner from "@/components/Banner.vue";
import RegResults from "@/components/reg_search/RegResults.vue";
import SearchInput from "@/components/SearchInput.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
        RegResults,
        SearchInput,
    },

    props: {},

    beforeCreate() {},

    async created() {
        // async calls here
        if (this.searchQuery) {
            this.retrieveSynonyms(this.searchQuery);
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
            queryParams: this.$route.query,
            results: [],
            synonyms: [],
            unquotedSearch: false,
            searchInputValue: undefined,
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
                this.results = [];
            }

            try {
                const response = await getRegSearchResults(query);
                this.results = response?.results ?? [];
            } catch (error) {
                console.error("Error retrieving regulation search results");
                this.results = [];
            } finally {
                this.isLoading = false;
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
                        this.results = [];
                        return;
                    }

                    this.retrieveRegResults(this.searchQuery);
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

    .results-container {
        overflow: auto;
        width: 100%;
        margin-bottom: 30px;

        .results-content {
            max-width: $text-max-width;
            margin: 0 auto;
            padding: 0 $spacer-5;
            @include screen-xl {
                padding: 0 $spacer-4;
            }

            .result {
                margin-top: 0px;
            }
        }
    }
}
</style>
