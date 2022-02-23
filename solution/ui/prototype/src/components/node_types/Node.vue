<template>
    <img v-if="node.node_type === 'Image'" :src="node.src" class="reg-image" />
    <component
        v-else
        :is="node.node_type"
        :node="node"
        :key="node.title"
    ></component>
</template>

<script>
export default {
    name: "Node",

    // https://v2.vuejs.org/v2/guide/components-edge-cases.html?redirect=true#Circular-References-Between-Components
    components: {
        SECTION: () => import("@/components/node_types/Section.vue"),
        SUBPART: () => import("@/components/node_types/Subpart.vue"),
        Paragraph: () => import("@/components/node_types/Paragraph.vue"),
        Extract: () => import("@/components/node_types/Extract.vue"),
        FlushParagraph: () =>
            import("@/components/node_types/FlushParagraph.vue"),
        Citation: () => import("@/components/node_types/Citation.vue"),
        FootNote: () => import("@/components/node_types/FootNote.vue"),
    },

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    computed: {
        componentType() {
            return this.node.node_type === "Image"
                ? "ImageComponent"
                : this.node.node_type;
        },
    },

    mounted() {
        this.$nextTick(() => {
            console.log(this.node.node_type);
        });
    },
};
</script>

<style></style>
