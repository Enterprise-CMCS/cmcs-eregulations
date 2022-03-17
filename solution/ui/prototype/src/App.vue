<template>
    <v-app>
        <router-view />
    </v-app>
</template>

<script>

export default {
    name: "App",
    components: {},
    created: function(){
      console.log("API URL: " + process.env.VUE_APP_API_URL)
    }
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
    box-sizing: border-box;
}

h1, h2, h3, h4, h5, h6, p, ul {
    margin-block-start: 1em;
    margin-block-end: 1em;
}

ul {
    padding-inline-start: 40px;
}
</style>
