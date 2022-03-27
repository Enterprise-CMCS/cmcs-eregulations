<template>
    <section
        :aria-labelledby="kebabTitle"
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section"
    >
        <h2 class="section-title" :id="kebabTitle">
            <button
                v-on:click="handleBtnClick"
                v-if="numSupplementalContent && !showResourceButtons"
                class="supplemental-content-count"
            >
                {{ numSupplementalContent }}
            </button>
            {{ node.title }}
        </h2>

        <div class="paragraphs">
            <template v-for="child in node.children">
                <Node
                    :node="child"
                    :key="child.title"
                    :showResourceButtons="showResourceButtons"
                    :supplementalContentCount="supplementalContentCount"
                />
            </template>
        </div>
        <div v-if="showResourceButtons && numSupplementalContent" class="btn-container">
            <ResourcesBtn
                :clickHandler="handleBtnClick"
                label="Section"
                size="small"
            />
        </div>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import { getKebabTitle, getDisplayName } from "@/utilities/utils.js";
import { getSupplementalContentNew } from "@/utilities/api";
export default {
    name: "Section",

    components: {
        Node,
        ResourcesBtn,
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
        resourceParamsEmitter: {
            type: Function,
            required: false,
        },
        showResourceButtons: {
            type: Boolean,
            required: false,
            default: true,
        },
        supplementalContentCount: {
            type: Object,
            required: false,
            default: () => {},
        },
    },

    data: () => ({
        supList: null,
    }),

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
        numSupplementalContent() {
            return this.supplementalContentCount
                ? this.supplementalContentCount[getDisplayName(this.node.label)]
                : 0;
        },
    },

    methods: {
        async handleBtnClick() {
            this.resourceParamsEmitter("section", [this.node.label[1]]);
        },
    },
    created(){
        this.resourceParamsEmitter("rendered", this.node.label[1]);
    }
};
</script>

<style>
.btn-container {
    margin: 20px 0px 50px;
}
.btn-container {
    margin: 20px 0px 50px;
}
.supplemental-content-count {
    background-color: #eefafe;
    color: #046791;
    padding: 3px 7px;
    border: #c0eaf8 solid 1px;
    border-radius: 3px;
    font-size: 12px;
    line-height: 20px;
}
</style>
