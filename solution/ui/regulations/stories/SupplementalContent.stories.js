import SupplementalContent from '../js/src/components/SupplementalContent.vue';
import {emptySupplementalContentResponse, supplementalContentResponse} from "./apiResponses";

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
    "api_url": "http://localhost:8000/v2/",
    "title": "42",
    "part": "433",
    "sections": ["100", "200", "300"],
    "getSupplementalContentLegacy": () => Promise.resolve(supplementalContentResponse)
};

export const EmptyCategories = Template.bind({});
EmptyCategories.args = {
    "api_url": "http://localhost:8000/v2/",
    "title": "42",
    "part": "433",
    "sections": ["100", "200", "300"],
    "getSupplementalContentLegacy": () => Promise.resolve(emptySupplementalContentResponse)
};
