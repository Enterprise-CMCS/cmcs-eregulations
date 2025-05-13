<script setup>
import { provide } from "vue";
import { getRecentResources } from "utilities/api";

import useFetch from "composables/fetch";

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

const rulesArgs = {
    page: 1,
    pageSize: 5,
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

</script>
<template>
    <div class="rules-container">
        <SimpleSpinner v-if="rulesResults.loading" />
        <RelatedRuleList
            v-if="!rulesResults.loading && type != 'supplemental'"
            :rules="rulesResults.data"
        />
        <RecentSupplementalContent
            v-if="!rulesResults.loading && type == 'supplemental'"
            :supplemental-content="rulesResults.data"
            :limit="5"
        />
    </div>
</template>
