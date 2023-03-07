<template>
    <div class="reg-results-container">
        <slot name="empty-state"></slot>
        <template v-for="(result, i) in results">
            <RegResultsItem
                :key="i"
                :base="base"
                :result="result"
                :query="query"
            />
        </template>
    </div>
</template>

<script>
import RegResultsItem from "@/components/reg_search/RegResultsItem.vue";

export default {
    name: "RegResults",

    components: {
        RegResultsItem,
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
        query: {
            type: String,
            default: "",
        },
    },
};
</script>

<style></style>
