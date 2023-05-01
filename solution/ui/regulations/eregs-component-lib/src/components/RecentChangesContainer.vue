<template>
    <div class="rules-container">

        <v-btn>Test</v-btn>
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList v-if="!loading" :rules="rules" />
    </div>
</template>

<script>
import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";

import { getFederalRegisterDocs } from "../api";

export default {
    name: "DefaultName",

    components: {
        RelatedRuleList,
        SimpleSpinner,
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
    },

    async created() {
        const rulesResponse = await getFederalRegisterDocs(this.apiUrl, {
            page: 1,
            pageSize: 3,
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

<style lang="scss">
.rules-container {
    margin: 12px 0;

    .related-rule-list {
        margin-top: 20px;
        margin-bottom: 40px;
    }
}
</style>
