<template>
    <div class="floating-btn-group">
        <BottomNavBtn direction="back" label="Subpart C" />
        <div class="vertical-rule"></div>
        <BottomNavBtn direction="forward" label="Subpart E" />
    </div>
</template>

<script>
import BottomNavBtn from "./BottomNavBtn.vue";

export default {
    name: "BottomNavBtnGroup",

    components: {
        BottomNavBtn,
    },

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
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.floating-btn-group {
    @include default-tooltip;

    display: flex;
    align-items: center;
    width: fit-content;

    .vertical-rule {
        border-left: 1px solid $pale_blue;
        height: 30px;
    }
}

</style>

