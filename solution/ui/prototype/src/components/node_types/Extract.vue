<template>
    <section v-html="node.content"></section>
</template>

<script>
export default {
    name: "Extract",

    props: {
        node: {
            type: Object,
            required: true,
        },
    },
};
</script>

<style lang="scss">
</style>
