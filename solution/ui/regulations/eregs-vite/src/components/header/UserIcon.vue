<script setup>
import { ref } from "vue";

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

const moreMenuExpanded = ref(false);

const accountClick = () => {
    moreMenuExpanded.value = !moreMenuExpanded.value;
};

const closeAccountClick = () => {
    moreMenuExpanded.value = false;
};
</script>

<template>
    <button class="user-account__button" @click="accountClick">
        <UserIconSvg />
    </button>
    <HeaderDropdownMenu
        v-if="moreMenuExpanded"
        class="dropdown-menu--account"
        @close-menu="closeAccountClick"
    >
        <template #dropdown-menu-content> Hello there </template>
    </HeaderDropdownMenu>
</template>

<style></style>
