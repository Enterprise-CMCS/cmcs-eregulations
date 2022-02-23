<template>
    <article>
        <h1 tabindex="-1" :id="kebabTitle">
            {{ node.title }}
        </h1>
        <template v-for="child in node.children">
            <Node 
                :node="child"
                :key="child.title"
            />
        </template>
    </article>
</template>

<script>
import Node from "@/components/node_types/Node.vue"
import { getKebabTitle } from "@/utilities/utils.js";

export default {
    name: "Subpart",

    components: {
        Node
    },

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
    },
};
</script>

<style></style>
