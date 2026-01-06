<script setup>
import { onMounted, onUnmounted } from 'vue';
import eventbus from "../eventbus";

const props = defineProps({
    trigger: {
        type: String,
        required: true,
    },
});

const handleScrollEnd = () => {
    console.info("scroll end reached");
    eventbus.emit("collapse-toggle", `${props.trigger} section history`);
};

const handleScrollTo = ({ trigger }) => {
    const element = document.querySelector(`[data-scroll-target='${trigger}']`);
    if (element && trigger === props.trigger) {
        window.addEventListener("scrollend", handleScrollEnd, { once: true });
        element.scrollIntoView({ behavior: "smooth" });
    }
};

onMounted(() => {
    eventbus.on("trigger-scroll-to", handleScrollTo);
});

onUnmounted(() => {
    eventbus.off("trigger-scroll-to", handleScrollTo);
});
</script>

<template>
    <slot />
</template>
