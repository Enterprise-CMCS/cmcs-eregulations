<template>
    <div class="floating-btn-group">
        <slot/>
    </div>
</template>

<script>

export default {
    name: "BottomNavBtnGroup",

    components: {},

    props: {},

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
.floating-btn-group {
    @include default-tooltip;

    display: flex;
    align-items: center;
    width: fit-content;
}

</style>

