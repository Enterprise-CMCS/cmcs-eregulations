<template>
    <div class="pagination-controls">
        <div class="left-control">
            <NavBtn direction="back" label="Previous" />
        </div>
        <div class="pages">1 2 3 4 5 ... 7</div>
        <div class="right-control">
            <NavBtn direction="forward" label="Next" />
        </div>
    </div>
</template>

<script>
import NavBtn from "@/components/floating_nav/NavBtn.vue";

export default {
    name: "PaginationController",

    components: {
        NavBtn,
    },

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

<style lang="scss">
    .pagination-controls {
        display: flex;
        justify-content: space-between;

        .left-control .icon {
            margin-left: 0;
        }

        .right-control .icon {
            margin-right: 0;
        }
    }
</style>

