<template>
    <article>
        <h1
            :id="kebabTitle"
            tabindex="-1"
        >
            <button
                v-if="numSupplementalContent"
                v-on:click="handleBtnClick"
                class="supplemental-content-count"
            >
                {{ numSupplementalContent }}
            </button>
            {{ node.title }}
        </h1>


        <div
            v-if="showResourceButtons"
            class="btn-container"
        >
            <ResourcesBtn
                :click-handler="handleBtnClick"
                label="Subpart"
            />
        </div>
        <template v-for="child in node.children">
            <Node
                :key="child.title"
                :node="child"
                :resource-params-emitter="resourceParamsEmitter"
                :show-resource-buttons="showResourceButtons"
                :supplemental-content-count="supplementalContentCount"
            />
        </template>
    </article>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import { getKebabTitle, getDisplayName } from "@/utilities/utils.js";

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
        },
        supplementalContentCount: {
            type:Object,
            required: false
        },

    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
        numSupplementalContent(){
            const total = this.node.children.reduce((count, node) => {
              return count + Number(this.supplementalContentCount[getDisplayName(node.label)] || 0)
            }, 0)
            console.log(total)
            return total
        }
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
