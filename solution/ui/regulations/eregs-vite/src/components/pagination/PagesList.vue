<template>
    <ul class="pages">
        <PageNumber
            v-for="pageNum in pagesArray"
            :key="pageNum"
            :current-page="currentPage"
            :number="pageNum"
        />
    </ul>
</template>

<script>
import PageNumber from "@/components/pagination/PageNumber.vue";

export default {
    name: "PagesList",

    components: {},

    props: {
        currentPage: {
            type: Number,
            required: false,
            default: 1,
        },
        pagesArray: {
            type: Array,
            required: false,
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

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style lang="scss" scoped>
ul.pages {
    padding: 0;
}
</style>
