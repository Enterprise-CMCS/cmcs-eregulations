<script>
    import CacheExplorer from "./views/CacheExplorer.vue";

    export default {
        name: "App",

        components: {
            CacheExplorer,
        }
    }
</script>

<template>
    <v-app>
        <CacheExplorer />
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
