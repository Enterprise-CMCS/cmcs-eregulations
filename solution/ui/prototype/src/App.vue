<template>
    <router-view />
</template>

<script>

export default {
    name: "App",
    components: {}
};

</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

*, ::before, ::after {
    box-sizing: unset;
}

input {
    background-color: white;
}

h1, h2, h3, h4, h5, h6, p, ul {
    margin-block-start: 1em;
    margin-block-end: 1em;
}

ul {
    padding-inline-start: 40px;
}
</style>
