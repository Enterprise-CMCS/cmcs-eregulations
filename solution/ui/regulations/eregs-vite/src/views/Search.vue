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
                                    <a :href="createSynonymQuotedLink(query)"
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
                                            :href="createSynonymQuotedLink(syn)"
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
                            eregs_url="/resources"
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
                                    :href="createResultLink(result)"
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

    created() {},

    beforeMount() {},

    mounted() {
        this.synonyms = this.getSynonyms();
        this.unquotedSearch = this.getUnquotedSearch();
        this.results = this.getResults();
        this.query = this.getQuery();
        this.searchInputValue = this.getQuery();
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            query: "",
            results: [],
            synonyms: [],
            unquotedSearch: false,
            searchInputValue: null,
        };
    },

    computed: {},

    methods: {
        getQuery() {
            if (!document.getElementById("query")) return "";

            const rawQuery = JSON.parse(
                document.getElementById("query").textContent
            );

            console.log("query", rawQuery);

            return rawQuery;
        },
        getResults() {
            if (!document.getElementById("results_list")) return "";

            const rawResults = JSON.parse(
                document.getElementById("results_list").textContent
            );

            console.log("rawResults", rawResults);

            return rawResults;
        },
        getSynonyms() {
            if (!document.getElementById("synonym_list")) return "";

            const rawSynonyms = JSON.parse(
                document.getElementById("synonym_list").textContent
            );

            console.log("rawSynonyms", rawSynonyms);

            return rawSynonyms;
        },
        getUnquotedSearch() {
            if (!document.getElementById("unquoted_search")) return "";

            const rawUnquotedBool = JSON.parse(
                document.getElementById("unquoted_search").textContent
            );

            console.log("rawUnquotedBool", rawUnquotedBool);

            return rawUnquotedBool;
        },
        stripQuotes(string) {
            return string.replace(/(^")|("$)/g, "");
        },
        createResultLink(props) {
            return `/${props.part_title}/${props.label[0]}/${props.label[1]}/${
                props.date
            }/?q=${props.q_list}#${props.label.join("-")}`;
        },
        createSynonymQuotedLink(val) {
            return `/search/?q=%22${val}%22`;
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
        },
        executeSearch() {
            if (!_isNull(this.searchInputValue)) {
                window.location.href = `/search/?q=${this.searchInputValue}`;
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

            .result {
                margin-top: 0px;
            }
        }
    }
}
</style>
