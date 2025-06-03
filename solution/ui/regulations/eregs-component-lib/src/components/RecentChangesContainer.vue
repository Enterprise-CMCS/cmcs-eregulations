<script setup>
import { provide } from "vue";
import { getRecentResources } from "utilities/api";

import useFetch from "composables/fetch";
import usePartsLastUpdated from "composables/partsLastUpdated.js";

import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import RecentSupplementalContent from "./RecentSupplementalContent.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    homeUrl: {
        type: String,
        required: false,
        default: "/",
    },
    type: {
        type: String,
        required: false,
        default: "rules",
    },
    categories: {
        type: String,
        required: false,
        default: null,
    },
});

provide("homeUrl", props.homeUrl);
provide("currentRouteName", "homepage");

const { partsLastUpdated, getPartsLastUpdated } = usePartsLastUpdated();

const rulesArgs = {
    page: 1,
    pageSize: 7,
    type: props.type,
};

if (props.type === "supplemental") {
    rulesArgs.categories = props.categories;
}

const rulesResults = useFetch({
    method: getRecentResources,
    apiUrl: props.apiUrl,
    args: rulesArgs,
});

getPartsLastUpdated({ apiUrl: props.apiUrl });
</script>

<template>
    <div class="rules-container">
        <SimpleSpinner v-if="rulesResults.loading || partsLastUpdated.loading" />
        <RelatedRuleList
            v-if="!rulesResults.loading && !partsLastUpdated.loading && type != 'supplemental'"
            :limit="rulesArgs.pageSize"
            :rules="rulesResults.data"
        />
        <RecentSupplementalContent
            v-if="!rulesResults.loading && !partsLastUpdated.loading && type == 'supplemental'"
            :parts-last-updated="partsLastUpdated.results"
            :limit="rulesArgs.pageSize"
            :supplemental-content="rulesResults.data"
        />
    </div>
</template>
