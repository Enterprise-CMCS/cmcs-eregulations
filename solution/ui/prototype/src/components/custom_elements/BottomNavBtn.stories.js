import BottomNavBtn from "./BottomNavBtn.vue";

export default {
    title: "Prototype/Components/Bottom Navigation Button",
    component: BottomNavBtn,
    argTypes: {
        direction: {
            name: "Direction of Movement",
            description: "Button to move backwards or forwards through subparts or sections",
            defaultValue: "forward",
            options: [
                "back",
                "forward"
            ],
            control: {
                type: "radio",
            },
        },
    },
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { BottomNavBtn },
    template: '<BottomNavBtn v-bind="$props" />',
});

export const Basic = Template.bind({});
