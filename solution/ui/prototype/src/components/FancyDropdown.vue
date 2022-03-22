<template>
    <div class="fancy-container">
        <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
                <label :for="buttonId">{{ label }}</label>
                <v-btn
                    :id="buttonId"
                    class="ds-c-field select-btn"
                    v-bind="attrs"
                    v-on="on"
                    depressed
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

    components: {},

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
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {},
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
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
