<template>
    <div class="part-nav-tabs" :class="partNavTabClasses">
        <div class="tabs-container">
            <div class="scroll-info" :class="scrollInfoClasses">
                <slot name="titlePart"></slot>
            </div>
            <slot name="tabs"></slot>
        </div>
    </div>
</template>

<script>
export default {
    components: {},

    name: "PartNav",

    props: {
        stickyMode: {
            validator: function (value) {
                return ["hideOnScrollDown", "normal", "disabled"].includes(
                    value
                );
            },
            default: "normal",
        },
        showHeader: {
            type: Boolean,
            default: true,
        },
        lastScrollPosition: {
            type: Number,
            default: 0,
        },
    },

    computed: {
        partNavTabClasses() {
            return {
                "top-header-hidden": !this.showHeader,
            };
        },
        scrollInfoClasses() {
            return {
                "is-pinned": this.lastScrollPosition >= 280, // magic number for now
            };
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

$sidebar-top-margin: 40px;

.part-nav-tabs {
    position: sticky;
    z-index: 1;
    background: $lightest_blue;
    transition: top 0.3s ease-in-out;

    top: $header_height_mobile;

    @include screen-lg {
        top: $header_height;
    }

    &.top-header-hidden {
        top: 0;
    }

    .tabs-container {
        display: flex;
        margin-left: 50px;
        max-width: $text-max-width;

        .scroll-info {
            display: none;
            overflow: hidden;

            &.is-pinned {
                display: flex;
                align-items: center;
                width: fit-content;
                padding-right: 20px;
                margin-right: 20px;
                border-right: 1px solid $light_gray;
                font-size: 18px;
                font-weight: 700;
            }
        }

        .nav-tabs.v-tabs {
            width: unset;
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

                .split-tab-container .split-tab-btn {
                    color: $mid_gray;
                }

                &.v-tab--active {
                    color: $teal_blue;
                    letter-spacing: 0.01em;
                    font-weight: 600;

                    .split-tab-container .split-tab-btn {
                        color: $teal_blue;
                    }
                }
            }

            .v-tabs-slider {
                background-color: $teal_blue;
            }
        }
    }
}
</style>
