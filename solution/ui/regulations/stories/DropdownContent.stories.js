import DropdownContent from '../js/src/components/DropdownContent.vue';
import DropdownHeader from '../js/src/components/DropdownHeader.vue';
import DropdownItem from '../js/src/components/DropdownItem.vue'

export default {
  title: 'Components/Dropdown/Dropdown Content',
  component: DropdownContent,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { DropdownContent, DropdownHeader, DropdownItem },
  template: `
  <dropdown-content v-bind="$props">
    <dropdown-header>Regulation Change</dropdown-header>
    <dropdown-item>Mar 1, 2021</dropdown-item>
    <dropdown-item>Jan 1, 2020</dropdown-item>
    <dropdown-item>May 3, 2019</dropdown-item>
  </dropdown-content>
  `,
});

export const Basic = Template.bind({});
Basic.args = {
  active: true,
};
