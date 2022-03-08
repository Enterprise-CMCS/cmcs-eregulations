<template>
    <section
        :aria-labelledby="kebabTitle"
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section"
    >
        <h2 class="section-title" :id="kebabTitle">
            <button v-on:click="handleBtnClick" v-if="numSupplementalContent" class="supplemental-content-count">{{numSupplementalContent}}</button> {{ node.title }}
        </h2>

        <div class="paragraphs">
            <template v-for="child in node.children">
                <Node :node="child" :key="child.title" :showResourceButtons="showResourceButtons" :supplementalContentCount="supplementalContentCount"/>
            </template>
        </div>
        <div v-if="showResourceButtons" class="btn-container">
            <ResourcesBtn :clickHandler="handleBtnClick" label="Section" />
        </div>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import { getKebabTitle, getDisplayName } from "@/utilities/utils.js";

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

          return this.supplementalContentCount[getDisplayName(this.node.label)]
        }
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
    .supplemental-content-count{
      background-color: #EEFAFE;
      color: #046791;
      padding: 3px 7px;
      border: #C0EAF8 solid 1px;
      border-radius: 3px;
      font-size: 12px;
      line-height: 20px;
    }
</style>
