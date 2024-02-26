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
        customLoginUrl: {
            type: String,
            default: "",
        },
        customUrl: {
            type: String,
            default: "",
        },
        homeUrl: {
            type: String,
            default: "",
        },
        searchUrl: {
            type: String,
            default: "",
        },
        statutesUrl: {
            type: String,
            default: "",
        },
        subjectsUrl: {
            type: String,
            default: "",
        },
        host: {
            type: String,
            default: "",
        },
        isAuthenticated: {
            type: Boolean,
            default: false,
        },
        hasEditableJobCode: {
            type: Boolean,
            default: false,
        },
    },
};
</script>

<template>
    <v-app>
        <router-view
            :api-url="apiUrl"
            :about-url="aboutUrl"
            :custom-login-url="customLoginUrl"
            :custom-url="customUrl"
            :home-url="homeUrl"
            :search-url="searchUrl"
            :statutes-url="statutesUrl"
            :subject-url="subjectsUrl"
            :host="host"
            :is-authenticated="isAuthenticated === 'True'"
            :has-editable-job-code="hasEditableJobCode === 'True'"
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
