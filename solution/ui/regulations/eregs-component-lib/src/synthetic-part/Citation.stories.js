import Citation from "./Citation.vue";
import { citations } from "legacy/msw/mocks/synthetic-part.js";

export default {
    title: "Prototype/Regulation Text/Nodes/Citation",
    component: Citation,
};

export const SyntheticCitation = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { Citation },
    template: `<Citation v-bind="$props"></Citation>`,
});

SyntheticCitation.args = { node: citations["499-21"] };
