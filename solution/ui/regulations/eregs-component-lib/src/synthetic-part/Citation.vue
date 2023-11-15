<template>
    <p>
        {{ node.content }}
    </p>
</template>

<script>
// TODO: implement citation templatetag logic from Django to create links

export default {
    name: "Citation",

    components: {
        Node,
    },

    props: {
        node: {
            type: Object,
            required: true,
        },
    },
};
</script>

<style></style>
