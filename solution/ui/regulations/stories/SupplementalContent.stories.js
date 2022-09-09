import { rest } from "msw";

import categories from "mocks/categories";
import toc from "mocks/toc";
import { locations, emptyLocations } from "mocks/locations";

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
            <script id="sub_categories" type="application/json">${JSON.stringify(
                []
            )}</script>
            <supplemental-content v-bind="$props" ></supplemental-content>
        </div>`,
});

export const Basic = Template.bind({});
Basic.args = {
    api_url: "http://localhost:8000/v3/",
    title: "42",
    part: "433",
    sections: ["100", "200", "300"],
    subparts: ["A"],
    getSupplementalContent: () => Promise.resolve(supplementalContentResponse),
};

export const EmptyCategories = Template.bind({});
EmptyCategories.args = {
    api_url: "http://localhost:8000/v3/",
    title: "42",
    part: "433",
    sections: ["100", "200", "300"],
    subparts: ["A"],
    getSupplementalContent: () =>
        Promise.resolve(emptySupplementalContentResponse),
};

EmptyCategories.parameters = {
    msw: {
        handlers: {
            supplementalContent: [
                rest.get(
                    "*/v3/resources/?locations=42.433.8&locations=42.433.10&locations=42.433.11&locations=42.433.15&locations=42.433.32&locations=42.433.34&locations=42.433.35&locations=42.433.36&locations=42.433.37&locations=42.433.38&locations=42.433.40&locations=42.433.A&paginate=true&location_details=false",
                    (req, res, ctx) =>
                        res(ctx.status(200), ctx.json(emptyLocations))
                ),
            ],
        },
    },
};
