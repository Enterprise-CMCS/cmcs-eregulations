<template>
    <section
        :aria-labelledby="nodeLabel"
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section"
    >
        <h2 class="section-title" :id="nodeLabel">
            {{ node.title }}
        </h2>

        <div class="paragraphs">
            <template v-for="child in node.children">
                <Node 
                    :node="child"
                    :key="child.title"
                />
            </template>
        </div>
    </section>
</template>

<script>
import Node from "@/components/node_types/Node.vue"

export default {
    name: "Section",

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
        kebabTitle() {
            console.log(this.node);
            return `${this.node.label.join("-")}-title`;
        },
    },
};
</script>

<style></style>
