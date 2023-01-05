<template>
    <div class="flash-banner" role="banner">
        <p>This is a CMCS project with draft content for CMCS staff.</p>
    </div>
</template>

<script>
export default {
    name: "FlashBanner",

    components: {},

    props: {
        propName: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        const container = document.getElementById("app-container");
        container.insertBefore(this.$el, container.firstChild);
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
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
};
</script>

<style></style>
