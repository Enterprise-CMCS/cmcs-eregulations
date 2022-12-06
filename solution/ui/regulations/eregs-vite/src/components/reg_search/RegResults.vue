<template>
    <div class="reg-results-container">
        <template v-if="results.length == 0">
            <SearchEmptyState
                :eregs_url="createRegulationsSearchUrl(base)"
                eregs_url_label="eRegulations resource links"
                eregs_sublabel="subregulatory guidance and implementation resources"
                :query="searchQuery"
            />
        </template>
        <template v-for="(result, i) in results" v-else>
            <RegResultsItem :key="i" :base="base" :result="result" />
        </template>
    </div>
</template>

<script>
import RegResultsItem from "@/components/reg_search/RegResultsItem.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";

export default {
    name: "RegResults",

    components: {
        RegResultsItem,
        SearchEmptyState,
    },

    props: {
        base: {
            type: String,
            required: true,
        },
        results: {
            type: Array,
            default: () => [],
        },
        searchQuery: String,
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        createRegulationsSearchUrl(base) {
            return `${base}/resources/`;
        },
    },
};
</script>

<style></style>
