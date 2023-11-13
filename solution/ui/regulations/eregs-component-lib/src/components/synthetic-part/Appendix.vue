<template>
    <section
        :aria-labelledby="kebabTitle"
        tabindex="-1"
        :id="kebabLabel"
        class="appendix-section"
    >
        <h2 class="section-title" :id="kebabLabel">
            {{ node.title }}
        </h2>

        <template v-for="(child, index) in node.children">
            <Node :node="child" :key="index" />
        </template>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import { getKebabLabel, getKebabTitle } from "@/utilities/utils.js";

export default {
    name: "Appendix",

    components: {
        Node,
    },

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    computed: {
        kebabLabel() {
            return getKebabLabel(this.node.label);
        },
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
    },
};
</script>

<style></style>
