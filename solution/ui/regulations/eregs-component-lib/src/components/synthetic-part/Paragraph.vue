<template>
    <p
        tabindex="-1"
        :id="kebabLabel"
        class="reg-section"
        :class="depthClass"
        v-html="node.text"
    ></p>
</template>

<script>
import { getKebabLabel, getParagraphDepth } from "@/utilities/utils.js";

export default {
    name: "Paragraph",

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    computed: {
        depthClass() {
            const depth = getParagraphDepth(this.node);
            return `depth-${depth}`;
        },
        kebabLabel() {
            return getKebabLabel(this.node.label);
        },
    },
};
</script>

<style></style>
