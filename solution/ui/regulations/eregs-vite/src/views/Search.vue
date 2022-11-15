<template>
    <body class="ds-base">
        <div id="searchApp" class="search-view">
            <Banner title="Search Results">
                <template #description>
                    <p>This site searches Title 42, Parts 400 and 430-460</p>
                    <p>{{ query }}</p>
                </template>
                <template #input>
                    <form class="search-form">
                        <v-text-field
                            id="main-content"
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
                        />
                    </form>
                </template>
            </Banner>
            <template v-for="result in results">
                <h3>Test</h3>
                <p>{{ result.parentHeadline }}</p>
            </template>
        </div>
    </body>
</template>

<script>
import Banner from "@/components/Banner.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
    },

    props: {},

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        this.results = this.getResults();
        this.query = this.getQuery();
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            query: "",
            results: [],
        };
    },

    computed: {
        parsedResults() {
            return JSON.parse(this.results);
        },
    },

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
}
</style>
