<template>
    <img v-if="node.node_type === 'Image'" :src="node.src" class="reg-image" />
    <component
        v-else
        :is="node.node_type"
        :node="node"
        :key="node.title"
        :resourceParamsEmitter="resourceParamsEmitter"
        :showResourceButtons="showResourceButtons"
        :supplementalContentCount="supplementalContentCount"
        :title="title"
        :part="part"
        :subpart="subpart"
        :headerLinks="headerLinks"
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
        SUBJGRP: () => import("@/components/node_types/SubjectGroup.vue"),
        SectionAuthority: () =>
            import("@/components/node_types/SectionAuthority.vue"),
        EffectiveDateNote: () =>
            import("@/components/node_types/EffectiveDateNote.vue"),
        APPENDIX: () => import("@/components/node_types/Appendix.vue"),
        Heading: () => import("@/components/node_types/Heading.vue"),
        Division: () => import("@/components/node_types/Division.vue"),
    },

    props: {
        title: {
            type: String,
            required: false,
        },
        part: {
            type: String,
            required: false,
        },
        node: {
            type: Object,
            required: true,
        },
        subpart:{
            type: String,
            required:false
        },
        headerLinks:{
            type: Boolean,
            required: false,
            default: false
        },
        resourceParamsEmitter: {
            type: Function,
            required: false,
        },
        showResourceButtons: {
            type: Boolean,
            required: false,
            default: true

        },
        supplementalContentCount: {
            type:Object,
            required: false,
            default: () => {}
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
            /*console.log(this.node.node_type);*/
        });
    },
};
</script>

<style></style>
