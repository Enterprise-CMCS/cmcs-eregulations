<template>
    <div>
        <div v-for="(category, index) in categoryList" :key="index">
            <div class="category">
                <collapse-button
                    v-bind:class="{ category: category }"
                    :name="category"
                    state="collapsed"
                    class="related-rules-title"
                >
                    <template v-slot:expanded
                        >{{ categories[category].title }}
                        <i class="fa fa-chevron-up category-toggle"></i
                    ></template>
                    <template v-slot:collapsed
                        >{{ categories[category].title }}
                        <i class="fa fa-chevron-down category-toggle"></i
                    ></template>
                </collapse-button>
                <collapsible
                    :name="category"
                    :state="
                        activeCategory === category ? 'expanded' : 'collapsed'
                    "
                >
                    <template v-if="isFetching">
                        <simple-spinner :size="'small'"></simple-spinner>
                    </template>
                    <template v-else>
                        <related-rule-list
                            :rules="getRules(category)"
                            :limit="limit"
                            :title="categories[category].title"
                        ></related-rule-list>
                    </template>
                </collapsible>
            </div>
        </div>
    </div>
</template>

<script>
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import RelatedRuleList from "./RelatedRuleList.vue";

export default {
    components: {
        CollapseButton,
        Collapsible,
        RelatedRuleList,
        SimpleSpinner,
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
            default: "",
        },
        categoryList: {
            type: Array,
            default: ["FINAL", "PROPOSED", "RFI"],
        },
        categories: {
            type: Object,
            default: {
                FINAL: {
                    getRules: (rules) => {
                        return rules.filter((rule) => {
                            return rule.type === "Rule";
                        });
                    },
                    title: "Final Rules",
                },
                PROPOSED: {
                    getRules: (rules) => {
                        return rules.filter((rule) => {
                            return (
                                rule.type === "Proposed Rule" &&
                                rule.action === "Proposed rule."
                            );
                        });
                    },
                    title: "Notices of Proposed Rulemaking",
                },
                RFI: {
                    getRules: (rules) => {
                        return rules.filter((rule) => {
                            return (
                                rule.type === "Proposed Rule" &&
                                rule.action === "Request for information."
                            );
                        });
                    },
                    title: "Requests for Information",
                },
            },
        },
    },

    data() {
        return {
            isFetching: true,
            limitedList: true,
            rules: [],
        };
    },

    computed: {},

    created() {
        this.fetch_rules(this.title, this.part);
    },

    methods: {
        async fetch_rules(title, part) {
            let url = `https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`;
            let results = [];
            while (url) {
                const response = await fetch(url);
                const rules = await response.json();
                results = results.concat(rules.results);
                url = rules.next_page_url;
            }
            this.rules = results;
            this.isFetching = false;
        },
        showCategory(category) {
            category === this.activeCategory
                ? (this.activeCategory = "")
                : (this.activeCategory = category);
        },
        buttonClass(category) {
            return this.categories[category].getRules(this.rules).length > 0
                ? "show-more-button"
                : "show-more-button show-more-inactive";
        },
        getRules(category) {
            return this.categories[category].getRules(this.rules);
        },
    },
};
</script>
