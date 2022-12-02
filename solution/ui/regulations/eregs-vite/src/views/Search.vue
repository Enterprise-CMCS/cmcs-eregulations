<template>
    <body class="ds-base search-page">
        <div id="searchApp" class="search-view">
            <Banner title="Search Results">
                <template #description>
                    <p>This site searches Title 42, Parts 400 and 430-460</p>
                </template>
                <template #input>
                    <form class="search-form" @submit.prevent="executeSearch">
                        <v-text-field
                            id="main-content"
                            :value="searchInputValue"
                            outlined
                            flat
                            solo
                            clearable
                            label="Search Regulations"
                            aria-label="Search Regulations"
                            type="text"
                            class="search-field shrink"
                            append-icon="mdi-magnify"
                            hide-details
                            dense
                            @input="updateSearchValue"
                            @click:append="executeSearch"
                            @click:clear="clearSearchQuery"
                        />
                        <div class="form-helper-text">
                            <template v-if="unquotedSearch">
                                <div class="search-suggestion">
                                    Didn't find what you were looking for? Try
                                    searching for
                                    <a
                                        :href="
                                            createSynonymQuotedLink(query, base)
                                        "
                                        >"{{ query }}"</a
                                    >
                                </div>
                            </template>
                            <template v-if="synonyms.length > 0">
                                <div class="search-suggestion">
                                    <span v-if="unquotedSearch">
                                        Or search
                                    </span>
                                    <span v-else> Search </span>
                                    for similar terms:
                                    <template v-for="(syn, i) in synonyms">
                                        <a
                                            :key="i"
                                            :href="
                                                createSynonymQuotedLink(
                                                    syn,
                                                    base
                                                )
                                            "
                                            >{{ syn }}</a
                                        ><span
                                            v-if="
                                                synonyms.length > 1 &&
                                                i + 1 < synonyms.length
                                            "
                                            :key="i"
                                            >,
                                        </span>
                                    </template>
                                </div>
                            </template>
                        </div>
                    </form>
                </template>
            </Banner>
            <div class="results-container">
                <div class="results-content">
                    <div class="search-results-count">
                        {{ results.length }} results in Medicaid & CHIP
                        Regulations
                    </div>
                    <template v-if="results.length == 0">
                        <SearchEmptyState
                            :eregs_url="createRegulationsSearchUrl(base)"
                            eregs_url_label="eRegulations resource links"
                            eregs_sublabel="subregulatory guidance and implementation resources"
                            :query="query"
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
    </body>
</template>

<script>
import _isNull from "lodash/isNull";

import Banner from "@/components/Banner.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
        SearchEmptyState,
    },

    props: {},

    beforeCreate() {},

    async created() {
        // async calls here
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
            query: "",
            results: [],
            synonyms: [],
            unquotedSearch: false,
            searchInputValue: "",
        };
    },

    computed: {},

    methods: {
        getQuery() {
            if (!document.getElementById("query")) return "";

            return JSON.parse(document.getElementById("query").textContent);
        },
        getResults() {
            if (!document.getElementById("results_list")) return [];

            return JSON.parse(
                document.getElementById("results_list").textContent
            );
        },
        getSynonyms() {
            if (!document.getElementById("synonym_list")) return [];

            return JSON.parse(
                document.getElementById("synonym_list").textContent
            );
        },
        getUnquotedSearch() {
            if (!document.getElementById("unquoted_search")) return false;

            return JSON.parse(
                document.getElementById("unquoted_search").textContent
            );
        },
        stripQuotes(string) {
            return string.replace(/(^")|("$)/g, "");
        },
        createResultLink(props, base) {
            return `${base}/${props.part_title}/${props.label[0]}/${
                props.label[1]
            }/${props.date}/?q=${props.q_list}#${props.label.join("-")}`;
        },
        createSynonymQuotedLink(val, base) {
            return `${base}/search/?q=%22${val}%22`;
        },
        createRegulationsSearchUrl(base) {
            return `${base}/search/`;
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
        },
        executeSearch() {
            if (!_isNull(this.searchInputValue)) {
                window.location.href = `${this.base}/search/?q=${this.searchInputValue}`;
            }
        },
        clearSearchQuery() {
            this.searchInputValue = "";
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
