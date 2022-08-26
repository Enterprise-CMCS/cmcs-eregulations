<template>
    <span class="page-number" :class="numberClasses">
        {{ number }}
    </span>
</template>

<script>
export default {
    name: "PageNumber",

    components: {},

    props: {
        number: {
            type: Number,
            required: false,
            default: 1,
        },
        selected: {
            type: Boolean,
            required: false,
            default: false,
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
        numberClasses() {
            return {
                selected: this.selected,
            };
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },

}
</script>

<style lang="scss" scoped>
.page-number {
    min-width: 44px;

    &.selected {
        font-weight: bold;
    }
}

</style>

