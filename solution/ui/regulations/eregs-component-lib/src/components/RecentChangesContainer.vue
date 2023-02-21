<template>
    <div class="rules-container">
        <span class="test-class">RED TEXT</span>
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList v-if="!loading" :rules="rules" />
    </div>
</template>

<script>
import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";

import { v3GetFederalRegisterDocs } from "../api";

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
        const rulesResponse = await v3GetFederalRegisterDocs(this.apiUrl, {
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
.test-class {
    color: red;
}
.rules-container {
    margin: 12px 0;

    .related-rule-list {
        margin-top: 20px;
        margin-bottom: 40px;
    }
}
</style>
