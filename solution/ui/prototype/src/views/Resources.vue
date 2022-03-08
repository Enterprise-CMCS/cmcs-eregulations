<template>
    <div>
        <h1>RESOURCES</h1>
        {{ queryParams }}
    </div>
</template>

<script>
export default {
    name: "Resources",

    components: {},

    props: {
        propName: {
            type: String,
            required: false,
            default: "default value",
        },
    },

    data() {
        return {
            queryParams: this.$route.query,
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

    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
                console.log("toParams in watch", toParams);
            },
        },
        "$route.query": {
            async handler(toQueries, previousQueries) {
                // react to route changes...
                console.log("toQueries in watch", toQueries);
            },
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
};
</script>

<style></style>
