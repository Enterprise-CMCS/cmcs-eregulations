<script>
export default {
    name: "App",

    components: {},
};
</script>

<template>
    <v-app>
        <router-view />
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

h1, h2, h3, h4, h5, h6, p, ul {
    margin-block-start: 1em;
    margin-block-end: 1em;
}

ul {
    padding-inline-start: 40px;
}
</style>
