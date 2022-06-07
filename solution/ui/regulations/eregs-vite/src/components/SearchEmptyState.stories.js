import SearchEmptyState from "./SearchEmptyState.vue";

export default {
    title: "Regulations/Search/Empty State",
    component: SearchEmptyState,
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { SearchEmptyState },
    template: '<SearchEmptyState v-bind="$props" />',
});

export const Basic = Template.bind({});
Basic.args = {
    eregs_url: "https://www.google.com",
    eregs_url_label: "eRegulations resource links",
    eregs_sublabel: "(subregulatory guidance and implementation resources)",
    query: "test",
};

