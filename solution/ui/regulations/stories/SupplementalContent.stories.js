import SupplementalContent from '../js/src/components/SupplementalContent.vue';

export default {
  title: 'SupplementalContent/SupplementalContent',
  component: SupplementalContent,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementalContent },
  template: '<supplemental-content v-bind="$props" ></supplemental-content>',
});

export const Basic = Template.bind({});
Basic.args = {
    "title": "43",
    "part": "433",
    "sections": ["100", "200", "300"]
};
