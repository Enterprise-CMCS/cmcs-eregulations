import RelatedRuleList from "../js/src/components/RelatedRuleList.vue";
import { relatedRulesResponse } from "./apiResponses";

export default {
    title: "Supplemental Resources/Related Rule List",
    component: RelatedRuleList,
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { RelatedRuleList },
    template: '<related-rule-list v-bind="$props" ></related-rule-list>',
});

export const Basic = Template.bind({});
Basic.args = {
    rules: relatedRulesResponse,
};
