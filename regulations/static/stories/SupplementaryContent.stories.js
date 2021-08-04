import SupplementaryContent from '../components/SupplementaryContent.vue';

export default {
  title: 'SupplementaryContent/SupplementaryContent',
  component: SupplementaryContent,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementaryContent },
  template: '<supplementary-content v-bind="$props" ></supplementary-content>',
});

export const Basic = Template.bind({});
Basic.args = {
    "title": "43",
    "part": "433",
    "sections": ["100", "200", "300"]
};
