<template>
    <div class="pagination-controls">
        <div class="left-control">Previous</div>
        <div class="pages">1 2 3 4 5 ... 7</div>
        <div class="right-control">Next</div>
    </div>
</template>

<script>
export default {
    name: "PaginationController",

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

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

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

}
</script>

<style>
    .pagination-controls {
        display: flex;
        justify-content: space-between;
    }
</style>

