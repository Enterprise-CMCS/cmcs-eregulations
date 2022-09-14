import Division from "./Division.vue";
import { tables } from "legacy/msw/mocks/synthetic-part.js";

export default {
    title: "Prototype/Regulation Text/Nodes/Table",
    component: Division,
};

export const SyntheticTable = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { Division },
    template: `<Division v-bind="$props"></Division>`,
});

SyntheticTable.args = { node: tables["499-52"] };
