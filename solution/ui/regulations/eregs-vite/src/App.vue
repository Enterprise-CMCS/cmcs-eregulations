<script>
    import HelloWorld from "./components/HelloWorld.vue";

    export default {
        name: "App",

        components: {
            HelloWorld,
        }
    }
</script>

<template>
    <div>
        <v-btn>Test 2</v-btn>
        <HelloWorld msg="Hello Vue 3 + Vite" />
    </div>
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
