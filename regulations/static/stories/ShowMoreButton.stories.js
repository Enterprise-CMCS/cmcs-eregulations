import ShowMoreButton from '../components/ShowMoreButton.vue'

export default {
  title: 'Button/Show More Button',
  component: ShowMoreButton,
}

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { ShowMoreButton },
  template: '<show-more-button v-bind="$props" ></show-more-button>',
});

export const Basic = Template.bind({});
Basic.args = {
  count: 5 
};
