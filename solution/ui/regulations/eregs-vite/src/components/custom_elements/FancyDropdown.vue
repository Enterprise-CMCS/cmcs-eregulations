<template>
    <div class="fancy-container">
        <v-menu offset-y max-width="240" max-height="460">
            <template v-slot:activator="{ on, attrs }">
                <label :for="buttonId">{{ label }}</label>
                <v-btn
                    :id="buttonId"
                    class="ds-c-field select-btn"
                    v-bind="attrs"
                    v-on="on"
                    depressed
                    :disabled="disabled"
                >
                    {{ buttonTitle }}
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
    },
};
</script>

<style lang="scss">
.fancy-container {
    flex: 1;

    @include screen-md {
        &:first-child {
            margin-right: 9px;
        }

        &:last-child {
            margin-left: 9px;
        }

        &:not(:first-child):not(:last-child) {
            margin: 0 9px;
        }
    }

    label {
        font-weight: bold;
        font-size: 14px;
    }

    button.v-btn.select-btn {
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
}
</style>
