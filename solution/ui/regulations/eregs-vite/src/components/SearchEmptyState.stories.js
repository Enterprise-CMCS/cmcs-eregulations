import SearchEmptyState from "./SearchEmptyState.vue";

export default {
    title: "Regulations/Search/Empty State",
    component: SearchEmptyState,
    argTypes: {
        eregs_url: {
            name: "eRegs URL",
            description: "URL for link to eRegs Search Page",
            defaultValue: "https://regulations-pilot.cms.gov/resources/",
            options: [
                "https://regulations-pilot.cms.gov/resources/",
                "https://regulations-pilot.cms.gov/search/",
            ],
            control: {
                type: "radio",
            },
        },
        eregs_url_label: {
            name: "eRegs Search Link Text",
            description: "Text for the link",
            defaultValue: "eRegulations resource links",
        },
        eregs_sublabel: {
            name: "eRegs Search Link parenthetical text",
            description: "additional label",
            defaultValue: "subregulatory guidance and implementation resources",
        },
        query: {
            name: "Search term",
            description: "word or phrase that will be used to perform search",
            defaultValue: "test",
        },
    },
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { SearchEmptyState },
    template: '<SearchEmptyState v-bind="$props" />',
});

export const Basic = Template.bind({});
