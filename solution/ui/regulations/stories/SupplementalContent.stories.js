import SupplementalContent from '../js/src/components/SupplementalContent.vue';
import {emptySupplementalContentResponse, supplementalContentResponse, categoryResponse} from "./apiResponses";
import {getSupplementalContentByCategory} from "../js/api";

export default {
  title: 'Supplemental Content/Supplemental Content',
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
    "getSupplementalContent": () => Promise.resolve(supplementalContentResponse)
};

export const EmptyCategories = Template.bind({});
EmptyCategories.args = {
    "api_url": "http://localhost:8000/v2/",
    "title": "42",
    "part": "433",
    "sections": ["100", "200", "300"],
    "getSupplementalContent": () => Promise.resolve(emptySupplementalContentResponse)
};

export const RulesOnly = Template.bind({});
RulesOnly.args = {
    "api_url": "http://localhost:8000/v2/",
    "title": "42",
    "part": "433",
    "sections": ["100", "200", "300"],
    "requested_categories": "1,2",
    "getSupplementalContentByCategory": () => Promise.resolve(categoryResponse)
};