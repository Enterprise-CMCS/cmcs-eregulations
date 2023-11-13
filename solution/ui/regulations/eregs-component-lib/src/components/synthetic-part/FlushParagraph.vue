<template>
    <section class="flush-paragraph-section">
        <div class="prototype-fp" v-html="node.content"></div>
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
