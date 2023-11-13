<template>
    <section class="flush-paragraph-section">
        <div class="synthetic-part-fp" v-html="node.content"></div>
    </section>
</template>

<script>
export default {
    name: "FlushParagraph",

    props: {
        node: {
            type: Object,
            required: true,
        },
    },
};
</script>

<style></style>
