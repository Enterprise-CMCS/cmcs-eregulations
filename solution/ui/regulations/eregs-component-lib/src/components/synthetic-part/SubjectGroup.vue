<template>
    <div>
        <section tabindex="-1" id="kebabLabel" class="reg-section">
            <h2 v-html="node.title"></h2>
            {{ node.text }}
        </section>

        <template v-for="child in node.children">
            <Node 
                :node="child"
                :key="child.title"
                :resource-params-emitter="resourceParamsEmitter"
                :showResourceButtons="showResourceButtons"
                :supplementalContentCount="supplementalContentCount"
                :subpart="subpart"
                :headerLinks="headerLinks"
            />
        </template>
    </div>
</template>

<script>
import Node from "@/components/node_types/Node.vue"
import { getKebabLabel } from "@/utilities/utils.js";

export default {
    name: "SubjectGroup",

    components: {
        Node
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
        subpart: {
            type:String,
            required: false
        },
        headerLinks:{
            type: Boolean,
            required: false,
            default: false
        }
    },

    computed: {
        kebabLabel() {
            return getKebabLabel(this.node.label);
        },
    },
}
</script>

<style>

</style>

