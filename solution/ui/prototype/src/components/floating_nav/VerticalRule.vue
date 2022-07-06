<template>
    <div class="vertical-rule"></div>
</template>

<script>
export default {
    name: "VerticalRule",

    components: {},

    props: {},
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.vertical-rule {
    border-left: 1px solid $pale_blue;
    height: 30px;
}
</style>
