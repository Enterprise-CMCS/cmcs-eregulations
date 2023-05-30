<template>
    <div v-if="prototype" class="rules-container homepage-updates">
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList v-if="!loading && type=='rules'" :rules="rules"/>
        <RecentSupplementalContent v-if="!loading && type!='rules'" :supplemental_content="rules"/>
    </div>
    <div v-else class="rules-container homepage-updates ds-l-col--4">
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList v-if="!loading" :rules="rules"/>
    </div>
</template>

<script>
import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import RecentSupplementalContent from "./RecentSupplementalContent.vue"
import { getRecentResources } from "../api";

export default {
    name: "DefaultName",

    components: {
        RelatedRuleList,
        SimpleSpinner,
        RecentSupplementalContent
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: false,
            default: ""
        },
        prototype: {
            type: Boolean,
            required: false,
            default: false
        },
    },

    async created() {
        const rulesResponse = await getRecentResources(this.apiUrl, {
            page: 1,
            pageSize: 3,
        }, this.type);

        this.rules = rulesResponse.results;
        this.loading = false;
    },

    data() {
        return {
            loading: true,
            rules: [],
        };
    },

    provide() {
        return {
            itemTitleLineLimit: 3,
        };
    },
};
</script>

<style lang="scss">
.rules-container {
    margin: 12px 0;

    .related-rule-list {
        margin-top: 20px;
        margin-bottom: 40px;
    }
}
</style>
