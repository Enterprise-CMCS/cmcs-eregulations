<template>
    <div class="flash-banner" role="banner">
        We welcome questions and suggestions --
        <BlockingModalTrigger
            trigger-label="give us feedback."
            modal-title="Feedback survey"
        ></BlockingModalTrigger
    </div>
</template>

<script>
import BlockingModalTrigger from "legacy/js/src/components/BlockingModalTrigger.vue";

export default {
    name: "FlashBanner",

    components: {
        BlockingModalTrigger,
    },

    props: {
        propName: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        const container = document.getElementById("app-container");
        container.insertBefore(this.$el, container.firstChild);
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style></style>
