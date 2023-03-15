<script>
export default {
    name: "App",

    components: {},

    props: {
        apiUrl: {
            type: String,
            default: "/v2/",
        },
        aboutUrl: {
            type: String,
            default: "/about/",
        },
        customUrl: {
            type: String,
            default: "",
        },
        homepageUrl: {
            type: String,
            default: "",
        },
        resourcesUrl: {
            type: String,
            default: "",
        },
        host: {
            type: String,
            default: "",
        },
    },
};
</script>

<template>
    <v-app>
        <router-view
            :api-url="apiUrl"
            :about-url="aboutUrl"
            :custom-url="customUrl"
            :homepage-url="homepageUrl"
            :resources-url="resourcesUrl"
            :host="host"
        />
    </v-app>
</template>

<style lang="scss">
*,
::before,
::after {
    box-sizing: unset;
}

input {
    background-color: white;
    box-sizing: border-box;
}

h1,
h2,
h3,
h4,
h5,
h6,
p,
ul {
    margin-block-start: 1em;
    margin-block-end: 1em;
}

ul {
    padding-inline-start: 40px;
}

.v-application {
    font-family: Open Sans, Helvetica, sans-serif;

    .v-application--wrap {
        min-height: unset;
    }
}
</style>
