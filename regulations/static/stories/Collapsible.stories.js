import CollapseButton from '../components/CollapseButton.vue';
import Collapsible from '../components/Collapsible.vue';

export default {
  title: 'Site/Collapsible',
  component: CollapseButton,
  subcomponents: { Collapsible },
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { CollapseButton, Collapsible },
  template: `
    <div>
      <collapse-button v-bind="$props" />
      <collapsible name="default" state="collapsed" direction="vertical">Hello, world!</collapsible>
      <hr />
      <collapsible name="default" state="collapsed" direction="horizontal">Hello world in horizontal</collapsible>
    </div>`,
});

export const Basic = Template.bind({});
Basic.args = {
    "name": "default",
    "state": "collapsed",
};
