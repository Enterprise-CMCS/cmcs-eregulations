<template>
    <section
        :aria-labelledby="kebabTitle"
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section"
    >
        <h2 class="section-title" :id="kebabTitle">
            {{ node.title }}
        </h2>

        <div class="paragraphs">
            <template v-for="child in node.children">
                <Node :node="child" :key="child.title" />
            </template>
        </div>
        <div class="btn-container">
            <ResourcesBtn :clickHandler="handleBtnClick" label="Section" />
        </div>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import { getKebabTitle } from "@/utilities/utils.js";

export default {
    name: "Section",

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
    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
    },

    methods: {
        handleBtnClick() {
            this.resourceParamsEmitter("section", this.node.label[1]);
        },
    },
};
</script>

<style>
    .btn-container {
        margin: 20px 0px 50px;
    }
</style>
