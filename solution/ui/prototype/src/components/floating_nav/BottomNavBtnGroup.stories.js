import BottomNavBtnGroup from "./BottomNavBtnGroup.vue";
import BottomNavBtn from "./BottomNavBtn.vue";
import VerticalRule from "./VerticalRule.vue";

export default {
    title: "Prototype/Components/Floating Bottom Navigation/Button Group",
    component: BottomNavBtnGroup,
    argTypes: {},
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { BottomNavBtn, BottomNavBtnGroup, VerticalRule },
    template: 
        `<BottomNavBtnGroup>
            <BottomNavBtn direction="back" label="Subpart C" />
            <VerticalRule />
            <BottomNavBtn direction="forward" label="Subpart E" />
        </BottomNavBtnGroup>`,
});

export const Basic = Template.bind({});
