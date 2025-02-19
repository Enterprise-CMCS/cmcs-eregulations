<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
const emit = defineEmits(["closeMenu"]);

const outsideClick = () => {
    emit("closeMenu");
};

const windowWidth = ref(window.innerWidth);
const appendPxSuffix = (int) => `${int}px`;
const positionStyle = computed(() => {
    return windowWidth.value > 1504
        ? { right: appendPxSuffix((windowWidth.value - 1440) / 2)}
        : {}
});

const onWidthChange = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => {
    window.addEventListener("resize", onWidthChange);
});
onUnmounted(() => window.removeEventListener("resize", onWidthChange));
</script>

<template>
    <div
        v-clickaway="outsideClick"
        class="dropdown-menu__container"
        :style="positionStyle"
    >
        <slot name="dropdown-menu-content" />
    </div>
</template>

<style></style>
