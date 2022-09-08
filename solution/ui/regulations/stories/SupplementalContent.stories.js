import categories from "mocks/categories";

import SupplementalContent from "../js/src/components/SupplementalContent.vue";
import {
    emptySupplementalContentResponse,
    supplementalContentResponse,
    categoryResponse,
} from "./apiResponses";

export default {
    title: "Supplemental Resources/Supplemental Content",
    component: SupplementalContent,
};

const Template = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { SupplementalContent },
    template: `<div>
            <script id="categories" type="application/json">${JSON.stringify(
                categories
            )}</script>
            <script id="sub_categories" type="application/json">${JSON.stringify([])}</script>
            <supplemental-content v-bind="$props" ></supplemental-content>
        </div>`,
});

export const Basic = Template.bind({});
Basic.args = {
    api_url: "http://localhost:8000/v2/",
    title: "42",
    part: "433",
    sections: ["100", "200", "300"],
    subparts: ["A"],
    getSupplementalContent: () => Promise.resolve(supplementalContentResponse),
};

export const EmptyCategories = Template.bind({});
EmptyCategories.args = {
    api_url: "http://localhost:8000/v2/",
    title: "42",
    part: "433",
    sections: ["100", "200", "300"],
    getSupplementalContent: () =>
        Promise.resolve(emptySupplementalContentResponse),
};