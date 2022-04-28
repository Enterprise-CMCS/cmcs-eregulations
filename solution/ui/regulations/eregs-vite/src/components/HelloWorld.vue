<template>
    <div>
        <h1>{{ msg }}</h1>

        <p>
            Recommended IDE setup:
            <a href="https://code.visualstudio.com/" target="_blank">VS Code</a>
            +
            <a href="https://github.com/johnsoncodehk/volar" target="_blank"
                >Volar</a
            >
        </p>

        <p>
            <a href="https://vitejs.dev/guide/features.html" target="_blank">
                Vite Documentation
            </a>
            |
            <a href="https://v3.vuejs.org/" target="_blank">Vue 3 Documentation</a>
        </p>

        <p>
            Edit
            <code>components/HelloWorld.vue</code> to test hot module replacement.
        </p>
    </div>
</template>

<script>
    export default {
        name: "HelloWorld",

        props: {
            msg: {
                type: String,
                default: "",
            }
        }
    }
</script>

<style scoped>
a {
    color: #42b983;
}
</style>
