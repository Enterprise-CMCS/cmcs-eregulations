<template>
    <div class="pagination-controls">
        <div class="left-control">
            <router-link
                :to="{
                    name: view,
                    query: { ...$route.query, page: page - 1 },
                }"
            >
                <NavBtn
                    direction="back"
                    label="Previous"
                    disabled="page == 1"
                />
            </router-link>
        </div>
        <ul class="pages">
            <li v-for="pageNum in pagesArr" :key="pageNum">
                <router-link
                    v-if="page != pageNum"
                    :to="{
                        name: view,
                        query: { ...$route.query, page: pageNum },
                    }"
                >
                    {{ pageNum }}
                </router-link>
                <span v-else class="current-page">
                    {{ pageNum }}
                </span>
            </li>
        </ul>
        <div class="right-control">
            <router-link
                :to="{
                    name: view,
                    query: { ...$route.query, page: page + 1 },
                }"
            >
                <NavBtn
                    direction="forward"
                    label="Next"
                    disabled="page == pagesArr[pagesArr.length - 1]"
                />
            </router-link>
        </div>
    </div>
</template>

<script>
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

<style lang="scss">
.pagination-controls {
    display: flex;
    justify-content: space-between;

    a {
        text-decoration: none;
    }

    .left-control .icon {
        margin-left: 0;
    }

    .right-control .icon {
        margin-right: 0;
    }

    ul.pages li {
        display: inline;
        list-style: none;
    }
}
</style>
