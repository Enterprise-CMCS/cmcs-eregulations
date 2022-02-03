---
to: ui/regulations/stories/<%= name %>Component.stories.js
---
import <%= name %>Component from '../js/src/components/<%= name %>Component.vue';

export default {
  title: '<%= name %>Component',
  component: <%= name %>Component,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { <%= name %>Component },
  template: '<<%= h.changeCase.lower(name) %>-component v-bind="$props" ></<%= h.changeCase.lower(name) %>-component>',
});

export const Basic = Template.bind({});
Basic.args = {};