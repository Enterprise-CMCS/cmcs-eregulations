<template>
    <iframe
        id="iframeEl"
        style="background-color: #DDEAFC"
        :title="title"
        width="100%"
        :src="src"
        frameborder="0"
        @load="onLoad"
    >
    </iframe>
</template>

<script>
export default {
    name: "IFrameContainer",

    components: {},

    props: {
        title: {
            type: String,
            default: "Iframe content",
        },
        src: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            isLoading: true,
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        onLoad() {
            this.isLoading = false;
        },
    },
};
</script>

<style></style>
