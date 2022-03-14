<template>
    <div class="nav-container">
        <div class="content" :class="filtersClass">
            <h1>Resources</h1>
            <slot></slot>
        </div>
    </div>
</template>

<script>
import InlineLoader from "@/components/InlineLoader.vue";

export default {
    name: "ResourcesNav",

    components: {},

    props: {
        resourcesDisplay: {
            type: String,
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

    computed: {
        filtersClass() {
            return `content-with-${this.resourcesDisplay}`;
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.nav-container {
    overflow: auto;
    width: 100%;
    background: $lightest_blue;

    .content-with-column {
        margin: 0 auto;
    }

    .content-with-sidebar {
        margin-left: 50px;
    }

    .content {
        max-width: $text-max-width;

        h1 {
            margin-top: 55px;
            margin-bottom: 40px;
        }
    }
}
</style>
