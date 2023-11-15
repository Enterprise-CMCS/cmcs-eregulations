import Appendix from "./Appendix.vue";
import { appendix } from "legacy/msw/mocks/synthetic-part.js";

export default {
    title: "Prototype/Regulation Text/Nodes/Appendix",
    component: Appendix,
};

export const SyntheticAppendix = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { Appendix },
    template: `<Appendix v-bind="$props"></Appendix>`,
});

SyntheticAppendix.args = { node: appendix };
