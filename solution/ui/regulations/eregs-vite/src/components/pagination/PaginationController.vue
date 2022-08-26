<template>
    <nav class="pagination-controls">
        <div class="left-control">
            <template v-if="page == 1">
                <NavBtn direction="back" label="Previous" is-disabled />
            </template>
            <template v-else>
                <router-link
                    :to="{
                        name: view,
                        query: { ...$route.query, page: page - 1 },
                    }"
                >
                    <NavBtn direction="back" label="Previous" />
                </router-link>
            </template>
        </div>
        <PagesList :current-page="page" :pages-array="pagesArr" />
        <div class="right-control">
            <template v-if="page == pagesArr[pagesArr.length - 1]">
                <NavBtn direction="forward" label="Next" is-disabled />
            </template>
            <template v-else>
                <router-link
                    :to="{
                        name: view,
                        query: { ...$route.query, page: page + 1 },
                    }"
                >
                    <NavBtn direction="forward" label="Next" />
                </router-link>
            </template>
        </div>
    </nav>
</template>

<script>
import PagesList from "@/components/pagination/PagesList.vue";
import NavBtn from "@/components/navigation/NavBtn.vue";

import { createOneIndexedArray } from "@/utilities/utils";

export default {
    name: "PaginationController",

    components: {
        NavBtn,
    },

    props: {
        count: {
            type: Number,
            required: false,
            default: 0,
        },
        page: {
            type: Number,
            required: false,
            default: 1,
        },
        pageSize: {
            type: Number,
            required: false,
            default: 100,
        },
        view: {
            type: String,
            required: true,
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

    computed: {
        pagesArr() {
            return createOneIndexedArray(Math.ceil(this.count / this.pageSize));
        },
    },
};
</script>

<style lang="scss" scoped>
nav.pagination-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;

    a {
        text-decoration: none;
    }

    .left-control .icon {
        margin-left: 0;
    }

    .right-control .icon {
        margin-right: 0;
    }
}
</style>
