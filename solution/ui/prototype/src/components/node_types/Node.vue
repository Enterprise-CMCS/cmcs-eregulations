<template>
    <component :is="node.node_type" :node="node" :key="node.title"></component>
</template>

<script>
export default {
    name: "Node",

    // https://v2.vuejs.org/v2/guide/components-edge-cases.html?redirect=true#Circular-References-Between-Components
    components: {
        SECTION: () => import("@/components/node_types/Section.vue"),
        SUBPART: () => import("@/components/node_types/Subpart.vue"),
        Paragraph: () => import("@/components/node_types/Paragraph.vue"),
    },

    props: {
        node: {
            type: Object,
            required: true
        }
    }
};
</script>

<style></style>
