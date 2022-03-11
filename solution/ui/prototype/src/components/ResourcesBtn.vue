<template>
    <v-btn
        :outlined="isOutlined"
        :depressed="isDepressed"
        :small="isSmall"
        class="resources-btn"
        @click="clickHandler"
    >
        View {{ label }} Resources
    </v-btn>
</template>

<script>
export default {
    name: "ResourcesBtn",

    props: {
        clickHandler: {
            type: Function,
            required: true,
        },
        label: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: false,
            default: "outlined",
        },
        size: {
            type: String,
            required: false,
        },
    },

    data() {
        return {
            isOutlined: this.type === "outlined",
            isDepressed: this.type === "solid",
            isSmall: this.size === "small",
        };
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

@mixin solid-btn {
    color: white;
    background-color: $mid_blue;
    border: 1px solid $mid_blue;
}

button.v-btn.resources-btn {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: normal;
    text-transform: capitalize;
    border: 1px solid $mid_blue;

    &.v-btn--outlined {
        color: $mid_blue;

        &:hover {
            @include solid-btn;
        }
    }

    &.v-btn--has-bg.theme--light {
        @include solid-btn;
    }
}
</style>
