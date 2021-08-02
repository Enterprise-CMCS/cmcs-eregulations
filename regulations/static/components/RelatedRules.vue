<template>
    <div>
        <related-rule-list :rules="limitedRules"></related-rule-list>
        <show-more-button :showMore="showMore" :count="rulesCount"></show-more-button>
    </div>
</template>

<script>
import RelatedRuleList from './RelatedRuleList.vue'
import ShowMoreButton from './ShowMoreButton.vue'
export default {
    components: {
        RelatedRuleList,
        ShowMoreButton,
    },

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        limit: {
            type: Number,
            default: 5,
        },
    },

    data() {
        return {
            rules: [],
            limitedList: true,
        }
    },

    computed: {
      limitedRules() {
        if(this.limitedList) {
          return this.rules.slice(0, this.limit);
        }
        return this.rules;
      },
      rulesCount() {
        return this.rules.length;
      }
    },

    async created() {
        this.rules = await this.fetch_rules(this.title, this.part);
    },

    methods: {
        async fetch_rules(title, part) {
            const response = await fetch(`https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[type][]=RULE&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`);
            const rules = await response.json();
            return rules.results;
        },
        showMore() {
          this.limitedList = !this.limitedList
        }
    }
};
</script>
