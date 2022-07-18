<template>
    <section :aria-labelledby="kebabTitle" tabindex="-1" :id="kebabTitle" class="reg-section">
        <h2 class="section-title" :id="kebabTitle">
            <button v-on:click="handleBtnClick" v-if="numSupplementalContent && !showResourceButtons"
                class="supplemental-content-count">
                {{ numSupplementalContent }}
            </button>
            <router-link v-if="node.children && headerLinks && !hideHyperlink" :to="{
                name: 'PDpart-section',
                params: { title: '42', part: this.node.label[0], subPart: this.formattedSubpart, section: this.node.label[1] }
            }">
                <v-tooltip top color="#EEFAFE">
                    <template v-slot:activator="{ on, attrs }">
                        <span v-bind="attrs" class="header-text" v-on="on">{{ node.title }}</span>
                    </template>
                    <span class="tooltip-text">View § {{this.node.label[0]}}.{{this.node.label[1]}}</span>
                </v-tooltip>
            </router-link>
            <span v-else>{{ node.title }}</span>
        </h2>

        <div class="paragraphs">
            <template v-for="child in node.children">
                <Node :node="child" :key="child.title" :showResourceButtons="showResourceButtons"
                    :supplementalContentCount="supplementalContentCount" />
            </template>
        </div>
        <div v-if="showResourceButtons && numSupplementalContent" class="btn-container">
            <ResourcesBtn :clickHandler="handleBtnClick" label="Section" size="small" />
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
        subpart: {
            type: String,
            required: false
        },
        node: {
            type: Object,
            required: true,
        },
        headerLinks:{
            type:Boolean,
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
            default: true,
        },
        supplementalContentCount: {
            type: Object,
            required: false,
            default: () => { },
        },
    },

    data: () => ({
        supList: null,
    }),

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
        hideHyperlink(){
            return this.$route.name === "PDpart-section"
        },
        formattedSubpart() {
            if(this.subpart){
               return this.subpart.includes("Subpart") ? this.subpart : 'Subpart-' + this.subpart 
            }
            return 'Subpart-undefined'
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
    created() {
        this.resourceParamsEmitter("rendered", this.node.label[1]);
    }
};
</script>

<style lang="scss">

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

.content-container .content .content-with-drawer {
    margin: 0;
}

.section-title a {
    text-decoration: none;
}

.v-tooltip__content {
    box-shadow: rgba(0, 0, 0, 0.3) 0 2px 10px;
    opacity: 1!important;
    background: #EEFAFE;
}

.tooltip-text {
    font-size: 12px !important;
    display: block !important;
    color: #212121;
}
.tooltip-text::after {
    border-right: solid 5px transparent;
    border-left: solid 5px transparent;
    border-top: solid 5px #EEFAFE;
    transform: translateX(-50%);
    position: absolute;
    z-index: -1;
    content: "";
    top: 100%;
    left: 50%;
    height: 0;
    width: 0;
}
</style>
