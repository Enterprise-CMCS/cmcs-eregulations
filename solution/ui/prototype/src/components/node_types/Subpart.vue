<template>
    <article>
        <h1 tabindex="-1" :id="kebabTitle">
            {{ node.title }}
        </h1>
        <div v-if="showResourceButtons" class="btn-container">
            <ResourcesBtn :clickHandler="handleBtnClick" label="Subpart" />
        </div>
        <template v-for="child in node.children">
            <Node
                :node="child"
                :key="child.title"
                :resourceParamsEmitter="resourceParamsEmitter"
                :showResourceButtons="showResourceButtons"
            />
        </template>
    </article>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import { getKebabTitle } from "@/utilities/utils.js";

export default {
    name: "Subpart",

    components: {
        Node,
        ResourcesBtn,
    },

    props: {
        node: {
            type: Object,
            required: true,
        },
        resourceParamsEmitter: {
            type: Function,
            required: false,
        },
        showResourceButtons: {
            type: Boolean,
            required: false,
            default: true
        }
    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
    },

    methods: {
        handleBtnClick() {
            this.resourceParamsEmitter("subpart", this.node.label[0]);
        },
    },
};
</script>

<style lang="scss">
</style>
