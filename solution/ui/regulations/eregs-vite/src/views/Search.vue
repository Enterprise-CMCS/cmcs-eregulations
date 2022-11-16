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
        stripQuotes(string) {
            return string.replace(/(^")|("$)/g, "");
        },
        createResultLink(props) {
            return `/${props.part_title}/${props.label[0]}/${props.label[1]}/${
                props.date
            }/?q=${props.q_list}#${props.label.join("-")}`;
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
        },
        executeSearch() {
            if (!_isNull(this.searchInputValue)) {
                window.location.href = `/search/?q=${this.searchInputValue}`
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
        .search-field {
            height: 40px;
            margin-bottom: 50px;
            .v-input__icon.v-input__icon--append button {
                color: $mid_blue;
            }
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
