<script setup>
import useDropdownMenu from "composables/dropdownMenu";

import HeaderDropdownMenu from "./HeaderDropdownMenu.vue";
import UserIconSvg from "../svgs/user-icon.vue";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

const { menuExpanded, toggleClick, closeClick } = useDropdownMenu();
</script>

<template>
    <button class="user-account__button" @click="toggleClick">
        <UserIconSvg />
    </button>
    <HeaderDropdownMenu
        v-if="menuExpanded"
        class="dropdown-menu--account"
        @close-menu="closeClick"
    >
        <template #dropdown-menu-content> Hello there </template>
    </HeaderDropdownMenu>
</template>

<style></style>
