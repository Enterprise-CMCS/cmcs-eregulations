<template>
    <div class="flash-banner" role="banner">
        <span class="greeting">We welcome questions and suggestions &mdash;</span>
        <BlockingModalTrigger
            trigger-label="give us feedback."
            modal-title="Feedback survey"
        />
    </div>
</template>

<script>
import BlockingModalTrigger from "./BlockingModalTrigger.vue";

const POSSIBLE_LOCATIONS = {
    django: "legacy django template",
    vite: "vite single page app",
};

export default {
    name: "FlashBanner",

    components: {
        BlockingModalTrigger,
    },

    props: {
        whereUsed: {
            validator: (value) =>
                Object.keys(POSSIBLE_LOCATIONS).includes(value),
            type: String,
            default: "django",
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        if (this.whereUsed === "vite") {
            const container = document.getElementById("app-container");
            container.insertBefore(this.$el, container.firstChild);
        }
    },

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
