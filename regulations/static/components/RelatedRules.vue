<template>

    <div>
      <div v-for="category in categoryList">
        <button @click="showCategory(category)" :class="buttonClass(category)" style="width:100%; text-align:left">
          {{categories[category].title}}
          <i v-if="activeCategory === category" class="fa fa-chevron-up" style="float:right"></i>
          <i v-else class="fa fa-chevron-down" style="float:right"></i>
        </button>
        <div v-if="activeCategory === category">
          <related-rule-list v-if="getRules(category).length > 0" :rules="getRules(category)"></related-rule-list>
          <div v-else>No {{categories[category].title}} found in the Federal Register from 1994 to present.</div>
        </div>
      </div>


    </div>
</template>

<script>
import RelatedRuleList from "./RelatedRuleList.vue";
import ShowMoreButton from "./ShowMoreButton.vue";

export default {
    components: {
        RelatedRuleList
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
        activeCategory: {
          type: String,
          default: ''
        },
        categoryList: {
          type: Array,
          default: ['FINAL', 'PROPOSED', 'RFI']
        },
        categories: {
          type: Object,
          default: {
            FINAL: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Rule'
                    }
                )
              },
              title: "Final Rules"
            },
            PROPOSED: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Proposed Rule' && rule.action === "Proposed rule."
                    }
                )
              },
              title: "Notification of Proposed Rulemaking"
            },
            RFI: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Proposed Rule' && rule.action === "Request for information."
                    }
                )
              },
              title: "Request for Information"
            }
          }
        },

    },

    data() {
        return {
            rules: [],
            limitedList: true,
        };
    },

    computed: {
        finalRules(){
          return this.categories.FINAL.getRules(this.rules)
        },
        proposedRules(){
            return this.categories.PROPOSED.getRules(this.rules)
        },
        RFIRules(){
            return this.categories.RFI.getRules(this.rules)
        },

    },

    async created() {
        this.rules = await this.fetch_rules(this.title, this.part);
    },

    methods: {
        async fetch_rules(title, part) {
          let url = `https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`
          let results = []

          while(url){
            const response = await fetch(url);
            const rules = await response.json();
            results = results.concat(rules.results)
            url = rules.next_page_url
          }
          return results

        },
        showCategory(category) {
          category === this.activeCategory ? this.activeCategory = '': this.activeCategory = category
        },
        buttonClass(category){
          return this.categories[category].getRules(this.rules).length > 0 ? "show-more-button": "show-more-button show-more-inactive"
        },
        getRules(category){
          return this.categories[category].getRules(this.rules)
        }

    },
};
</script>
