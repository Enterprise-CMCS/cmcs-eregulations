<template>
    <div class="pagination-controls">
        <div class="left-control">
            <NavBtn direction="back" label="Previous" />
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
            <NavBtn direction="forward" label="Next" />
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
            type: String,
            required: false,
            default: "1",
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

    methods: {
        goToPage(e) {
            console.log(e);
            this.$router.push({ query: { ...this.$route.query, page: 3 } });
        },
    },
};
</script>

<style lang="scss">
.pagination-controls {
    display: flex;
    justify-content: space-between;

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
