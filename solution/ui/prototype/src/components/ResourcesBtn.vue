<template>
    <v-btn outlined small @click="clickHandler">
        View {{ label }} Resources
    </v-btn>
</template>

<script>
export default {
    name: "ResourcesBtn",

    props: {
        clickHandler: {
            type: Function,
            required: true
        },
        label: {
            type: String,
            required: true
        }
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

button.v-btn.v-btn--outlined {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: normal;
    color: $mid_blue;
    border: 1px solid $mid_blue;
    text-transform: capitalize;
}
</style>
