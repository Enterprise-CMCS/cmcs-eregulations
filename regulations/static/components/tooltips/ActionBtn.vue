<template>
    <button
        class="action-btn"
        :class="buttonClasses"
        @click="handleClick"
        :disabled="selected && this.status === 'success'"
    >
        <svg
            v-if="selected && this.status === 'success'"
            width="17"
            height="17"
            viewBox="0 0 17 17"
        >
            <svg width="17" height="17">
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M8.50007 16C4.36452 16 1 12.6355 1 8.50007C1 4.36452 4.36452 1 8.50007 1C12.6355 1 15.9999 4.36452 15.9999 8.50007C15.9999 12.6355 12.6355 16 8.50007 16ZM8.50007 2.02937C4.93206 2.02937 2.02922 4.93221 2.02922 8.50007C2.02922 12.0681 4.93206 14.9708 8.50007 14.9708C12.0679 14.9708 14.9706 12.0681 14.9706 8.50007C14.9706 4.93221 12.0679 2.02937 8.50007 2.02937Z"
                    fill="#2A7A3B"
                    stroke="#2A7A3B"
                    stroke-width="0.25"
                />
            </svg>
            <svg width="17" height="17" x="4" y="5">
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M3.48221 5.98237C3.34562 5.98237 3.21476 5.92812 3.11831 5.83166L1.2191 3.93246C1.01811 3.73161 1.01811 3.40565 1.2191 3.2048C1.4201 3.00366 1.74577 3.00366 1.94676 3.2048L3.48221 4.73996L7.05287 1.1693C7.25357 0.968307 7.57954 0.968307 7.78053 1.1693C7.98152 1.37014 7.98152 1.69611 7.78053 1.89696L3.84597 5.83166C3.74951 5.92812 3.61866 5.98237 3.48221 5.98237Z"
                    fill="#2A7A3B"
                    stroke="#2A7A3B"
                    stroke-width="0.25"
                />
            </svg>
        </svg>
        {{ label }}
    </button>
</template>

<script>
export default {
    name: "action-button",

    props: {
        actionType: {
            type: String,
            required: true,
        },
        selectedAction: {
            type: String,
            required: true,
        },
        status: {
            type: String,
            required: true,
        },
    },

    computed: {
        selected() {
            return (
                this.selectedAction === this.actionType &&
                this.status !== "idle"
            );
        },
        labelState() {
            return this.selected && this.status === "success"
                ? "copied"
                : "copy";
        },
        label() {
            return `${this.labelState} ${this.actionType}`;
        },
        buttonClasses() {
            return {
                "selected-btn": this.selected && this.status === "success",
                "default-btn": !this.selected,
            };
        },
    },

    methods: {
        handleClick() {
            this.$emit("action-btn-click", {
                actionType: this.actionType,
            });
        },
    },

    filters: {},
};
</script>
