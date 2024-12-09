<script setup>
const emit = defineEmits(["closeMenu"]);

const outsideClick = () => {
    emit("closeMenu");
};
</script>

<template>
    <div v-clickaway="outsideClick" class="dropdown-menu__container">
        <slot name="dropdown-menu-content"></slot>
    </div>
</template>

<style></style>
