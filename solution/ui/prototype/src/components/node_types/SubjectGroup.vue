<template>
    <div>
        <section tabindex="-1" id="kebabLabel" class="reg-section">
            <h2> {{ node.title }} </h2>
            {{ node.text }}
        </section>

        <template v-for="child in node.children">
            <Node 
                :node="child"
                :key="child.title"
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

