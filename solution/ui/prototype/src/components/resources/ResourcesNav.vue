<template>
    <div class="nav-container">
        <div class="content" :class="filtersClass">
            <h1>Resources</h1>
            <p class="descriptive-text">
                Resources are curated and updated by a Medicaid subject matter
                expert. Final Rules, NPRMs, and RFIs  are automatically pulled
                from the
                <a href="https://www.federalregister.gov/" target="_blank"
                    >Federal Register</a
                >.
            </p>
            <slot></slot>
        </div>
    </div>
</template>

<script>

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
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
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
            margin-top: 45px;
            margin-bottom: 15px;
        }

        p.descriptive-text {
            margin-bottom: 30px;
        }

        a::after {
            @include external-link;
        }
    }
}
</style>
