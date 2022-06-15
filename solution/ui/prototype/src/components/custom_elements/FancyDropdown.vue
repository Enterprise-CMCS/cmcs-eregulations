<template>
    <div class="fancy-container" :class="containerClass">
        <v-menu offset-y max-width="240" max-height="460">
            <template v-slot:activator="{ on, attrs }">
                <label v-if="label" :for="buttonId">{{ label }}</label>
                <v-btn
                    :id="buttonId"
                    :class="btnTypeClass"
                    v-bind="attrs"
                    v-on="on"
                    depressed
                    :disabled="disabled"
                >
                    {{ buttonTitle }}
                    <i
                        v-if="type === 'splitTab'"
                        class="fa fa-chevron-down"
                    ></i>
                </v-btn>
            </template>
            <slot></slot>
        </v-menu>
    </div>
</template>

<script>
export default {
    name: "FancyDropdown",

    props: {
        label: {
            type: String,
            default: "",
        },
        buttonTitle: {
            type: String,
            default: "Select",
        },
        buttonId: {
            type: String,
            default: "",
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        type: {
            type: String,
            required: false,
        },
    },

    computed: {
        btnTypeClass() {
            return this.type === "splitTab" ? "split-tab-btn" : "select-btn ds-c-field";
        },
        containerClass() {
            return this.type === "splitTab" ? "split-tab-container" : "";
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

.fancy-container {
    flex: 1;

    &:first-child {
        margin-right: 9px;
    }

    &:last-child {
        margin-left: 9px;
    }

    &:not(:first-child):not(:last-child) {
        margin: 0 9px;
    }

    label {
        font-weight: bold;
        font-size: 14px;
    }

    &.split-tab-container {
        margin: 0;
    }

    button.v-btn {
        &.select-btn {
            background-color: #fff;
            background-image: url(#{$eregs-image-path}/arrow-both.svg);
            background-position: right 10px center;
            border: 1px solid $light_gray;
            height: 36px;
            border-radius: 3px;
            padding: 0 0 0 10px;

            span.v-btn__content {
                font-size: 14px;
                display: flex;
                flex-direction: row;
                justify-content: flex-start;
                letter-spacing: initial;
                color: $dark_gray;
                text-transform: capitalize;

                i.v-icon {
                    color: $mid_gray;
                    margin-right: 5px;
                }
            }
        }

        &.split-tab-btn {
            border-radius: 0;
            border: none;
            background-color: transparent;
            padding: 0;
            margin: 0 0 0 10px;
            height: 48px;
            min-width: 35px;

            .v-btn__content {
                height: 60%;
                border-left: 1px solid #9D9D9D;
            }
        }
    }
}
</style>
