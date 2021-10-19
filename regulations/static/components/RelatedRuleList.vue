<template>
    <div class="related-rule-list" v-if="rules.length">
        <related-rule v-for="(rule, index) in limitedRules" :key="index"
            :title="rule.title"
            :type="rule.type"
            :citation="rule.citation"
            :publication_date="rule.publication_date"
            :document_number="rule.document_number"
            :html_url="rule.html_url"
            :action="rule.action"
        >
        </related-rule>
        <show-more-button
          v-if="rules.length > limit"
          :showMore="showMore"
          :count="rules.length"
        ></show-more-button>
    </div>
    <div v-else class="show-more-inactive">No {{title}} found in the Federal Register from 1994 to present.</div>

</template>

<script>
import RelatedRule from './RelatedRule.vue'
import ShowMoreButton from "./ShowMoreButton.vue";
export default {
    name: 'related-rule-list',

    components: {
        RelatedRule,
        ShowMoreButton
    },

    props: {
        rules: Array,
        limit: {
          type: Number,
          default: 5
        },
        title: {
          type: String,
        }

    },

    computed: {
        limitedRules() {
            if (this.limitedList) {
                return this.rules.slice(0, this.limit);
            }
            return this.rules;
        },
        rulesCount() {
            return this.rules.length;
        },
    },

    data() {
      return {
          limitedList: true,
      };
    },

    methods: {
        showMore() {
            this.limitedList = !this.limitedList;
        },
    },

    filters: {

    },
};
</script>
