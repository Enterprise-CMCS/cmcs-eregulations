import BottomNavBtnGroup from "./BottomNavBtnGroup.vue";
import NavBtn from "./NavBtn.vue";
import VerticalRule from "./VerticalRule.vue";

export default {
    title: "Regulations/Components/Floating Bottom Navigation/Button Group",
    component: BottomNavBtnGroup,
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
    components: { NavBtn, BottomNavBtnGroup, VerticalRule },
    template:
        `<BottomNavBtnGroup>
            <NavBtn v-bind="$props"/>
        </BottomNavBtnGroup>`,
});

Back.args = {
    direction: "back",
    label: "Subpart A",
};

export const Forward = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { NavBtn, BottomNavBtnGroup, VerticalRule },
    template:
        `<BottomNavBtnGroup>
            <NavBtn v-bind="$props"/>
        </BottomNavBtnGroup>`,
});

Forward.args = {
    direction: "forward",
    label: "Subpart C",
};

export const BackAndForward = (args) => ({
    components: { NavBtn, BottomNavBtnGroup, VerticalRule },
    template:
        `<BottomNavBtnGroup>
            <NavBtn direction="back" label="Subpart C" />
            <VerticalRule />
            <BottomNavBtn direction="forward" label="Subpart E" />
        </BottomNavBtnGroup>`,
});

BackAndForward.parameters = {
    controls: {
        hideNoControlsWarning: true,
        include: [],
    }
}
