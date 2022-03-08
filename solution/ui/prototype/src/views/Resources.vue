<template>
    <h1>RESOURCES</h1>
</template>

<script>
export default {
    name: "Resources",

    components: {},

    props: {
        propName: {
            type: String,
            required: false,
            default: "default value"
        },
    },

    data() {
        return {
            dataProp: "value",
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

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},
}
</script>

<style>

</style>

