<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";
import {
    getCurrentPageResultsRange,
} from "utilities/utils";

import PolicyResultsList from "./PolicyResultsList.vue";

const props = defineProps({
    categories: {
        type: Array,
        default: () => [],
    },
    results: {
        type: Array,
        default: () => [],
    },
    resultsCount: {
        type: Number,
        default: 0,
    },
    page: {
        type: String,
        default: "1",
    },
    pageSize: {
        type: Number,
        default: 10,
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
    hasEditableJobCode: {
        type: Boolean,
        default: false,
    },
    searchQuery: {
        type: String,
        default: "",
    },
    selectedSubjectParts: {
        type: Array,
        default: () => [],
    },
});

const $route = useRoute();

const apiUrl = inject("apiUrl");
const homeUrl = inject("homeUrl");

const currentPageResultsRange = getCurrentPageResultsRange({
    count: props.resultsCount,
    page: props.page,
    pageSize: props.pageSize,
});
</script>

<template>
    <div class="doc__list">
        <div class="search-results-count">
            <div class="count__info-row">
                <div class="count__info">
                    <span v-if="results.length > 0">{{ currentPageResultsRange[0] }} -
                        {{ currentPageResultsRange[1] }} of</span>
                    {{ resultsCount }} <span v-if="searchQuery">result</span><span v-else>document</span>
                    <span v-if="results.length != 1">s</span>
                </div>
            </div>
            <slot name="sign-in-cta" />
        </div>
        <slot name="empty-state" />
        <PolicyResultsList
            v-if="results.length > 0"
            :api-url="apiUrl"
            :categories="categories"
            :has-editable-job-code="hasEditableJobCode"
            :home-url="homeUrl"
            :parts-last-updated="partsLastUpdated"
            :query="$route.query.q"
            :results-list="results"
        />
    </div>
</template>
