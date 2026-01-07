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

const onIntersect = (isIntersecting) => {
    if (isIntersecting) {
        eventbus.emit("scroll-trigger-visible", {
            trigger: props.trigger,
        });
    }
};
</script>

<template>
    <button
        v-intersect.once="onIntersect"
        class="btn link-btn scroll-trigger__button"
        @click="clickHandler"
    >
        {{ label }}
    </button>
</template>
