<template>
    <div class="direction-btn" :class="directionClass">
        <span class="label">{{ label }}</span>
        <span class="icon">
            <i class="fa" :class="chevronClass"></i>
        </span>
    </div>
</template>

<script>
export default {
    name: "NavBtn",

    components: {},

    props: {
        direction: {
            type: String,
            required: true,
            default: "forward",
        },
        label: {
            type: String,
            required: true,
            default: "Loading...",
        },
        isDisabled: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    computed: {
        chevronClass() {
            return this.direction === "forward"
                ? "fa-chevron-right"
                : "fa-chevron-left";
        },
        directionClass() {
            return {
                [`${this.direction}-btn`]: true,
                disabled: this.isDisabled,
            };
        },
    },
};
</script>

<style lang="scss" scoped>
.direction-btn {
    border: none;
    background: none;
    cursor: pointer;
    color: $mid_blue;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    font-size: 14px;
    padding: 12px 0;

    .label {
        font-weight: 400;
    }

    .icon {
        margin: 0 10px -2px;
    }

    &.disabled {
        color: $mid_gray_3;
        cursor: default;
    }
}

.forward-btn {
    flex-direction: row;

    .icon {
        margin-right: 0px;
    }

    .label {
        padding-left: 10px;
    }
}

.back-btn {
    flex-direction: row-reverse;

    .icon {
        margin-left: 0px;
    }

    .label {
        padding-right: 10px;
    }
}
</style>
