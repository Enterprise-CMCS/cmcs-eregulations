<template>
    <div class="flash-banner" role="banner">
        <span class="greeting">We welcome questions and suggestions &mdash;&nbsp;</span>
        <BlockingModalTrigger
            trigger-label="give us feedback."
            modal-title="Feedback survey"
        />
    </div>
</template>

<script>
import BlockingModalTrigger from "./BlockingModalTrigger.vue";

export default {
    name: "FlashBanner",

    components: {
        BlockingModalTrigger,
    },

    props: {},

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {},

    computed: {},

    methods: {},
};
</script>

<style></style>
