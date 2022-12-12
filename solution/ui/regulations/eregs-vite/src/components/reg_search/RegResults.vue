<template>
    <div class="reg-results-container">
        <slot name="empty-state"></slot>
        <template v-for="(result, i) in results">
            <RegResultsItem :key="i" :base="base" :result="result" />
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

    methods: {},
};
</script>

<style></style>
