import DropdownHeader from '../eregs-component-lib/src/components/DropdownHeader.vue';

export default {
  title: 'Components/Dropdown/Dropdown Header',
  component: DropdownHeader,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { DropdownHeader },
  template: '<dropdown-header v-bind="$props" >{{ slotcontent }}</dropdown-header>',
});

export const Basic = Template.bind({});
Basic.args = {
  slotcontent: "Regulation Change"
};
