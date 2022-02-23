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
            <Node 
                :node="child"
                :key="index"
            />
        </template>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue"

export default {
    name: "Appendix",

    components: {
        Node
    },

    props: {
        node: {
            type: Object,
            required: true
        }
    },

    computed: {
        kebabLabel() {
            return `${this.node.label.join("-")}`;
        },
        kebabTitle() {
            return `${this.node.label.join("-")}-title`;
        },
    },
};
</script>

<style></style>
