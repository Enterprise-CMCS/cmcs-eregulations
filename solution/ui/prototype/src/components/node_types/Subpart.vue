<template>
    <article>
        <h1 tabindex="-1" :id="kebabTitle" class="subpart-title">
            <button v-if="numSupplementalContent && !showResourceButtons" v-on:click="handleBlueBtnClick"
                class="supplemental-content-count">
                {{ numSupplementalContent }}
            </button>
            <span v-if="!headerLinks || hideHyperlink">{{node.title}}</span>
            <router-link v-else :to="{
                name: 'PDpart-subPart',
                params: { title: this.title, part: this.part, subPart: 'Subpart-' + this.node.label[0] }
            }">
                <v-tooltip top color="#EEFAFE">
                    <template v-slot:activator="{ on, attrs }">
                        <span v-bind="attrs" v-on="on">{{ node.title }}</span>
                    </template>
                    <span class="tooltip-text">View Subpart {{this.node.label[0]}}</span></v-tooltip>
            </router-link>
        </h1>
        <div v-if="showResourceButtons && numDirectContent" class="btn-container">
            <ResourcesBtn :clickHandler="handleBtnClick" label="Subpart" size="small" />
        </div>
        <template v-for="child in node.children">
            <Node :node="child" :subpart="node.label[0]" :key="child.title"
                :resource-params-emitter="resourceParamsEmitter" :showResourceButtons="showResourceButtons" :headerLinks="headerLinks"
                :supplementalContentCount="supplementalContentCount" />
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
        title: {
            type: String,
            required: false,
        },
        part: {
            type: String | Number,
            required: false,
        },
        node: {
            type: Object,
            required: true,
        },
        headerLinks: {
            types: Boolean,
            required: false,
            default: false,
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
            type: Object,
            required: false,
            default: () => { }
        },

    },

    computed: {
        kebabTitle() {
            return getKebabTitle(this.node.label);
        },
        hideHyperlink(){
            return this.$route.name =='PDpart-subPart'
        },
        numSupplementalContent() {
            let total = 0
            if (this.supplementalContentCount && this.node.children) {

                total = this.node.children.reduce((count, node) => {
                    return count + Number(this.supplementalContentCount[getDisplayName(node.label)] || 0)
                }, 0)
            }
            return total
        },
        numDirectContent() {
            return this.supplementalContentCount[`${this.title} ${this.part} Subpart ${this.node.label[0]}`]
        }
    },

    methods: {
        handleBtnClick() {
            this.resourceParamsEmitter("subpart", [this.node.label[0]]);
        },
        handleBlueBtnClick() {
            this.resourceParamsEmitter(
                "subpart",
                {
                    subPart: this.node.label[0],
                    sections: this.node.children.filter(c => c.label).map(child => child.label[1])
                }
            );
        }
    },
};
</script>

<style lang="scss">
.subpart-title a {
    text-decoration: none;
}

.v-tooltip__content {
    box-shadow: rgba(0, 0, 0, 0.3) 0 2px 10px;
    background: #EEFAFE;
}
</style>
