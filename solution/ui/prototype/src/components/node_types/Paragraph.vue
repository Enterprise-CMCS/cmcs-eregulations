<template>
    <p
        tabindex="-1"
        :id="kebabTitle"
        class="reg-section depth-1"
    >
        {{ node.text }}
    </p>
</template>

<script>
export default {
    name: "Paragraph",

    components: {},

    props: {
        node: {
            type: Object,
            required: true,
        },
    },

    computed: {
        kebabTitle() {
            return `${this.node.label.join("-")}-title`;
        },
    },
};
</script>

<style></style>
