<template>
    <section class="footnote-section">
        <p v-html="node.content"></p>
    </section>
</template>

<script>
export default {
    name: "FootNote",

    props: {
        node: {
            type: Object,
            required: true,
        },
    },
};
</script>

<style></style>
