<template>
    <div id="app">
        <ResourcesNav />
    </div>
</template>

<script>
import ResourcesNav from "@/components/resources/ResourcesNav.vue";

export default {
    name: "Resources",

    components: {
        ResourcesNav,
    },

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
            API_URL: import.meta.env.VITE_API_URL,
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

