<script>
import { getRecentResources } from "utilities/api";
import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import RecentSupplementalContent from "./RecentSupplementalContent.vue";

export default {
    name: "DefaultName",

    components: {
        RelatedRuleList,
        SimpleSpinner,
        RecentSupplementalContent,
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: false,
            default: "rules",
        },
    },

    async created() {
        const categories =
            this.type === "supplemental"
                ? {
                      categories:
                          "&categories=5&categories=7&categories=6&categories=9&categories=10&categories=138&categories=8",
                  }
                : {};

        const rulesResponse = await getRecentResources(this.apiUrl, {
            page: 1,
            pageSize: 3,
            type: this.type,
            ...categories,
        });

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
<template>
    <div class="rules-container">
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList
            v-if="!loading && type != 'supplemental'"
            :rules="rules"
        />
        <RecentSupplementalContent
            v-if="!loading && type == 'supplemental'"
            :supplemental-content="rules"
        />
    </div>
</template>

<style lang="scss">
.rules-container {
    margin: 12px 0;

    .related-rule-list {
        margin-top: 20px;
        margin-bottom: 40px;
    }
}
</style>
