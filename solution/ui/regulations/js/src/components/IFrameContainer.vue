<template>
    <iframe
        id="iframeEl"
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
        src: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            isLoading: true,
            iframeHeight: 0,
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        onLoad(e) {
            console.log("onload event argument", e);
            const iframeEl = document.getElementById("iframeEl");
            console.log("iframeEl stuff", iframeEl.contentWindow.top.document.documentElement);
            /*this.iframeHeight = iframeEl.contentWindow.top.document.documentElement.scrollHeight;*/
            this.isLoading = false;
        },
    },
};
</script>

<style></style>
