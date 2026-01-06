<script setup>
import { onMounted, onUnmounted, useTemplateRef } from 'vue';
import eventbus from "../eventbus";

const props = defineProps({
    trigger: {
        type: String,
        required: true,
    },
});

const target = useTemplateRef(`scroll-target-${props.trigger}`);

const handleScrollEnd = () => {
    eventbus.emit(
        "collapse-toggle",
        {
            name: `${props.trigger} section history`,
            action: "expand",
        }
    );
};

const handleScrollTo = ({ trigger }) => {
    if (trigger === props.trigger) {
        window.addEventListener("scrollend", handleScrollEnd, { once: true });
        target.value.scrollIntoView({ behavior: "smooth" });
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
    <div
        ref="target"
        class="scroll-target-container"
    >
        <slot />
    </div>
</template>
