import PartContent from "./PartContent.vue";
import { fullPart } from "legacy/msw/mocks/synthetic-part.js";

export default {
    title: "Prototype/Regulation Text/Synthetic Part",
    component: PartContent,
};

export const Part499 = (args, { argTypes }) => ({
    props: Object.keys(argTypes),
    components: { PartContent },
    template: `<PartContent v-bind="$props"></PartContent>`,
});

Part499.args = { 
    title: fullPart.title,
    part: fullPart.label[0],
    subpart: "",
    structure: fullPart.children,
    resourcesDisplay: "drawer",
    showResourceButtons: false,
};
