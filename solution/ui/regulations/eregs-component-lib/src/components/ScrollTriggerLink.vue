<script setup>
import eventbus from "../eventbus";

const props = defineProps({
    label: {
        type: String,
        required: true,
    },
    trigger: {
        type: String,
        required: true,
    },
});

const clickHandler = () => {
    eventbus.emit("trigger-scroll-to", {
        trigger: props.trigger,
    });
};
</script>

<template>
    <button
        class="btn link-btn scroll-trigger__button"
        @click="clickHandler"
    >
        {{ label }}
    </button>
</template>
