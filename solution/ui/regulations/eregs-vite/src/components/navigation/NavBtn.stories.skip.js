import NavBtn from "./NavBtn.vue";

export default {
    title: "Regulations/Components/Floating Bottom Navigation/Button",
    component: NavBtn,
    argTypes: {
        direction: {
            name: "Direction of Movement",
            description:
                "Styles button to indicate if moving backwards or forwards through subparts or sections",
            defaultValue: "forward",
            options: ["back", "forward"],
            control: {
                type: "radio",
            },
        },
        label: {
            name: "Section or Subpart Label",
            description: "Button label to indicate if stepping through Subparts or Sections",
            defaultValue: "Subpart B",
        },
    },
};

export const Back = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { NavBtn },
    template: '<NavBtn direction="back" label="Subpart A" />',
});
Back.parameters = {
    controls: {
        hideNoControlsWarning: true,
        include: [],
    }
}

export const Forward = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { NavBtn },
    template: '<NavBtn direction="forward" label="Subpart B" />',
});
Forward.parameters = {
    controls: {
        hideNoControlsWarning: true,
        include: [],
    }
}

export const Interactive = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { NavBtn },
    template: '<NavBtn v-bind="$props" />',
});

