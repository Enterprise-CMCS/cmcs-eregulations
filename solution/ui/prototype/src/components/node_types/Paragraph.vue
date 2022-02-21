<template>
    <p
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section"
        :class="depthClass"
        v-html="node.text"
    ></p>
</template>

<script>
import { getParagraphDepth } from "@/utilities/utils.js";

export default {
    name: "Paragraph",

    components: {},

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    mounted() {
        this.$nextTick(() => {
            /*console.log(this.node)*/
        });
    },

    computed: {
        depthClass() {
            const depth = getParagraphDepth(this.node);
            return `depth-${depth}`;
        },
        kebabTitle() {
            return `${this.node.label.join("-")}-title`;
        },
    },
};
</script>

<style></style>
