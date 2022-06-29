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
.direction-btn {
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
