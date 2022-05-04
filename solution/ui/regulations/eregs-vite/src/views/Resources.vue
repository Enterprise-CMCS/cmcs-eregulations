<template>
    <div id="app">
        {{ PR }}
        RESOURCES
        <v-btn>TEST BUTTON</v-btn>
    </div>
</template>

<script>
export default {
    name: "Resources",

    components: {},

    props: {
        propName: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {
        console.log("import.meta", import.meta.env);
    },

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            PR: import.meta.env.VITE_PR,
        }
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },

}
</script>

<style>

</style>

