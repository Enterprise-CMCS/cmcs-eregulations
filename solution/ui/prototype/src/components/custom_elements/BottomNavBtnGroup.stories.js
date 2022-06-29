import BottomNavBtnGroup from "./BottomNavBtnGroup.vue";

export default {
    title: "Prototype/Components/Floating Bottom Navigation/Button Group",
    component: BottomNavBtnGroup,
    //argTypes: {
        //direction: {
            //name: "Direction of Movement",
            //description:
                //"Styles button to indicate if moving backwards or forwards through subparts or sections",
            //defaultValue: "forward",
            //options: ["back", "forward"],
            //control: {
                //type: "radio",
            //},
        //},
        //label: {
            //name: "Section or Subpart Label",
            //description: "Button label to indicate if stepping through Subparts or Sections",
            //defaultValue: "Subpart B",
        //},
    //},
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { BottomNavBtnGroup },
    template: '<BottomNavBtnGroup v-bind="$props" />',
});

export const Basic = Template.bind({});
