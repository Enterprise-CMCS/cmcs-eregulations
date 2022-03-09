<template>
    <article>
        <h1 tabindex="-1" :id="kebabTitle">
            <button
                v-if="numSupplementalContent"
                v-on:click="handleBtnClick"
                class="supplemental-content-count"
            >
                {{ numSupplementalContent }}
            </button>
            {{ node.title }}
        </h1>
        <div v-if="showResourceButtons" class="btn-container">
            <ResourcesBtn
                :clickHandler="handleBtnClick"
                label="Subpart"
                size="small"
            />
        </div>
        <template v-for="child in node.children">
            <Node
                :node="child"
                :key="child.title"
                :resource-params-emitter="resourceParamsEmitter"
                :showResourceButtons="showResourceButtons"
                :supplementalContentCount="supplementalContentCount"
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
            required: false,
            default: () => {}
        },

    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
        numSupplementalContent(){
          let total = 0
          if (this.supplementalContentCount && this.node.children ) {

            total = this.node.children.reduce((count, node) => {
              return count + Number(this.supplementalContentCount[getDisplayName(node.label)] || 0)
            }, 0)
          }
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

<style lang="scss"></style>
