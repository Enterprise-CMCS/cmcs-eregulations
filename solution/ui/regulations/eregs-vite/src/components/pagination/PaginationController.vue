<script setup>
import { computed } from "vue";
import { createOneIndexedArray } from "utilities/utils";
import PagesList from "@/components/pagination/PagesList.vue";
import NavBtn from "@/components/navigation/NavBtn.vue";

const props = defineProps({
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
});

const pagesArr = computed(() => {
    return createOneIndexedArray(Math.ceil(props.count / props.pageSize));
});
</script>

<template>
    <nav class="pagination-controls" aria-label="Pagination">
        <div class="pagination-control left-control">
            <template v-if="page == 1">
                <NavBtn
                    direction="back"
                    label="Previous"
                    is-disabled
                />
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
        <div class="pagination-control right-control">
            <template v-if="page == pagesArr[pagesArr.length - 1]">
                <NavBtn
                    direction="forward"
                    label="Next"
                    is-disabled
                />
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
