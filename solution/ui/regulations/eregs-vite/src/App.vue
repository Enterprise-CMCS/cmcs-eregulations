<script>
    import Resources from "./views/Resources.vue";

    export default {
        name: "App",

        components: {
            Resources,
        }
    }
</script>

<template>
    <v-app>
        <Resources />
    </v-app>
</template>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
}
</style>
