<script setup>
import eventbus from "../eventbus";

const props = defineProps({
    trigger: {
        type: String,
        required: true,
    },
});

const clickHandler = () => {
    console.info("Emitting scroll to trigger:", props.trigger);
    eventbus.emit("trigger-scroll-to", {
        trigger: props.trigger,
    });
};
</script>

<template>
    <div
        class="skeleton"
        @click="clickHandler"
    >
        Click me
    </div>
</template>
