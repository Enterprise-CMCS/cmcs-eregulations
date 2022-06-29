<template>
    <div class="direction-btn" :class="directionClass">
        <span class="label-span">{{ direction }}</span>
        <i class="fa" :class="chevronClass"></i>
    </div>
</template>

<script>
export default {
    name: "BottomNavBtn",

    components: {},

    props: {
        direction: {
            type: String,
            required: true,
            default: "forward",
        },
    },

    computed: {
        chevronClass() {
            return this.direction === "forward"
                ? "fa-chevron-right"
                : "fa-chevron-left";
        },
        directionClass() {
            return `${this.direction}-btn`;
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.direction-btn {
    background: $mid_blue;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    width: 106px;
    font-size: 14px;
    font-weight: 400;
    padding: 10px;

    .label-span {}
}

.forward-btn {
    flex-direction: row;
}

.back-btn {
    flex-direction: row-reverse;
}
</style>
