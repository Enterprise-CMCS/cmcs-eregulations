<template>
    <div v-if="rules.length" class="related-rule-list">
        <template v-for="(rule, i) in limitedRules" :key="i">
            <related-rule
                :title="ruleTitle(rule)"
                :type="type(rule)"
                :citation="citation(rule)"
                :publication_date="publication_date(rule)"
                :document_number="rule.document_number"
                :html_url="html_url(rule)"
                :action="rule.action"
            />
            <template v-if="rule.related_resources && rule.related_resources.length > 0">
                <related-rule
                    v-for="(related_resource, ii) in rule.related_resources"
                    :key="ii + 'grouped' + related_resource.document_number"
                    :title="ruleTitle(related_resource)"
                    :type="type(related_resource)"
                    :citation="citation(related_resource)"
                    :publication_date="publication_date(related_resource)"
                    :document_number="related_resource.document_number"
                    :html_url="html_url(related_resource)"
                    :action="related_resource.action"
                    grouped
                />
            </template>
        </template>
        <collapse-button
            v-if="showMoreNeeded"
            :name="innerName"
            state="collapsed"
            class="category-title"
        >
            <template #expanded>
                <show-more-button
                    button-text="- Show Less"
                    :count="rules.length"
                ></show-more-button>
            </template>
            <template #collapsed>
                <show-more-button
                    button-text="+ Show More"
                    :count="rules.length"
                ></show-more-button>
            </template>
        </collapse-button>
        <collapsible
            :name="innerName"
            state="collapsed"
            class="collapse-content additional-rules"
            overflow
        >
            <template v-for="(rule, i) in additionalRules" :key="i">
                <related-rule
                    :title="ruleTitle(rule)"
                    :type="type(rule)"
                    :citation="citation(rule)"
                    :publication_date="publication_date(rule)"
                    :document_number="rule.document_number"
                    :html_url="html_url(rule)"
                    :action="rule.action"
                >
                </related-rule>
                <template
                    v-if="rule.related_resources && rule.related_resources.length > 0"
                >
                    <related-rule
                        v-for="(related_resource, ii) in rule.related_resources"
                        :key="ii + 'grouped' + related_resource.document_number"
                        :title="ruleTitle(related_resource)"
                        :type="type(related_resource)"
                        :citation="citation(related_resource)"
                        :publication_date="publication_date(related_resource)"
                        :document_number="related_resource.document_number"
                        :html_url="html_url(related_resource)"
                        :action="related_resource.action"
                        grouped
                    />
                </template>
            </template>
            <collapse-button
                v-if="showMoreNeeded && rulesCount > 10"
                :name="innerName"
                state="collapsed"
                class="category-title"
            >
                <template #expanded>
                    <show-more-button
                        button-text="- Show Less"
                        :count="rules.length"
                    ></show-more-button>
                </template>
                <template #collapsed>
                    <show-more-button
                        button-text="+ Show More"
                        :count="rules.length"
                    ></show-more-button>
                </template>
            </collapse-button>
        </collapsible>
    </div>
    <div v-else class="show-more-inactive">
        No {{ title }} found in the Federal Register from 1994 to present.
    </div>
</template>

<script>
import RelatedRule from "./RelatedRule.vue";
import ShowMoreButton from "./ShowMoreButton.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

export default {
    name: "RelatedRuleList",

    components: {
        RelatedRule,
        ShowMoreButton,
        CollapseButton,
        Collapsible,
    },

    props: {
        rules: {
            type: Array,
            default: () => [],
        },
        limit: {
            type: Number,
            default: 5,
        },
        title: {
            type: String,
            default: "results",
        },
    },

    data() {
        return {
            limitedList: true,
            innerName: "RelatedRuleCollapsible",
        };
    },

    computed: {
        limitedRules() {
            return this.rules.slice(0, this.limit);
        },
        additionalRules() {
            return this.rules.slice(this.limit);
        },
        rulesCount() {
            return this.rules.length;
        },
        showMoreNeeded() {
            return this.rulesCount > this.limit;
        },
    },

    methods: {
        showMore() {
            this.limitedList = !this.limitedList;
        },
        ruleTitle(rule) {
            return rule.title || rule.description;
        },
        type(rule) {
            if (rule.withdrawal) {
                return "WD";
            }
            if (rule.correction) {
                return "CORR";
            }
            return rule.action_type || rule.category?.name || rule.type;
        },
        citation(rule) {
            return rule.citation || rule.document_id;
        },
        html_url(rule) {
            return rule.html_url || rule.url;
        },
        publication_date(rule) {
            return rule.publication_date || rule.date;
        },
    },
};
</script>
