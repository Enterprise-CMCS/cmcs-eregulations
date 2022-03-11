<template>
    <div class="nav-container">
        <div class="content" :class="resourcesClass">
            <h1>
                <span> {{ title }} CFR Part {{ part }} - </span>
                <span v-if="partLabel">{{ partLabel }}</span>
                <span v-else>
                    <InlineLoader />
                </span>
            </h1>
            <slot></slot>
        </div>
    </div>
</template>

<script>
import InlineLoader from "@/components/InlineLoader.vue";

export default {
    components: {
        InlineLoader,
    },

    name: "PartNav",

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        partLabel: {
            type: String,
        },
        resourcesDisplay: {
            type: String,
        },
    },

    computed: {
        resourcesClass() {
            return `content-with-${this.resourcesDisplay}`;
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

    .content-with-drawer {
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

        .nav-tabs.v-tabs .v-tabs-bar {
            background-color: transparent;

            .v-tab {
                color: $mid_gray;
                text-transform: none;
                font-weight: 500;
                padding: 0;
                margin-right: 35px;
                min-width: unset;
                letter-spacing: 0.02em;
                font-size: 18px;

                &.v-tab--active {
                    color: $teal_blue;
                    letter-spacing: 0.01em;
                    font-weight: 600;
                }
            }

            .v-tabs-slider {
                background-color: $teal_blue;
            }
        }
    }
}
</style>
