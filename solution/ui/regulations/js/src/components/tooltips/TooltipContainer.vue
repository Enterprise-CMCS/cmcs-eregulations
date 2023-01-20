<template>
    <div
        v-show="entered && btn_type === 'icon'"
        class="copy-tooltip hovered"
        :class="tooltipClasses"
        :style="tooltipStyles"
    >
        <slot name="tooltip-content"
    </div>
</template>

<script>
export default {
    name: "TooltipContainer",

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
        tooltipClasses() {
            return {
                "tooltip-caret": this.leftSafe,
                "tooltip-caret-left": !this.leftSafe,
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

<style>

</style>

