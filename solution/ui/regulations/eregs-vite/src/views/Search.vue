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
                    <div v-if="!isLoading">
                        <template v-if="results.length == 0">
                            <SearchEmptyState
                                :eregs_url="createRegulationsSearchUrl(base)"
                                eregs_url_label="eRegulations resource links"
                                eregs_sublabel="subregulatory guidance and implementation resources"
                                :query="searchQuery"
                            />
                        </template>
                        <template v-for="(result, i) in results" v-else>
                            <div :key="i" class="result">
                                <div class="results-part">
                                    {{ result.part_document_title }}
                                </div>
                                <div class="results-section">
                                    <a
                                        :href="createResultLink(result, base)"
                                        v-html="stripQuotes(result.parentHeadline)"
                                    />
                                </div>
                                <div
                                    class="results-preview"
                                    v-html="result.headline"
                                />
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </body>
</template>

<script>
import _isNull from "lodash/isNull";
import _isEmpty from "lodash/isEmpty";

import Banner from "@/components/Banner.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SearchInput from "@/components/SearchInput.vue";

import { getRegSearchResults, getSynonyms } from "@/utilities/api";

export default {
    name: "SearchView",

    components: {
        Banner,
        SearchEmptyState,
        SearchInput,
    },

    props: {},

    beforeCreate() {},

    async created() {
        // async calls here
        if (this.queryParams.q) {
            this.retrieveSynonyms(this.queryParams.q);
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
                const synonyms = await getSynonyms(this.stripQuotes(query));

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
        stripQuotes(string) {
            return string.replace(/(^")|("$)/g, "");
        },
        createResultLink(props, base) {
            return `${base}/${props.part_title}/${props.label[0]}/${
                props.label[1]
            }/${props.date}/?q=${props.q_list}#${props.label.join("-")}`;
        },
        createRegulationsSearchUrl(base) {
            return `${base}/resources/`;
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
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
                console.log("oldParams", oldParams);
                console.log("newParams", newParams);
                console.log("new q === old q", newParams.q === oldParams.q);
                if (newParams.q !== oldParams.q) {
                    if (_isEmpty(newParams.q)) {
                        this.results = [];
                        return;
                    }

                    this.retrieveRegResults(newParams.q);
                    this.retrieveSynonyms(newParams.q);
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

        .search-field {
            height: 40px;

            .v-input__icon.v-input__icon--append button {
                color: $mid_blue;
            }
        }

        .form-helper-text {
            margin-top: 10px;
        }
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
