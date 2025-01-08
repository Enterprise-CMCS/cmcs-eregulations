<script setup>
import { computed } from "vue";
import HeaderLink from "./header/HeaderLink.vue";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
});

const getAccessUrl = computed(() => `${props.base}get-account-access/`);

const isActive = window.location.pathname.includes("get-account-access");

const propsObj = {
    name: "get-account-access",
    active: isActive,
    href: getAccessUrl.value,
};
</script>

<template>
    <HeaderLink
        v-bind="propsObj"
        class="header__access-link header__access-link--narrow"
        label="Get Access"
    />
    <HeaderLink
        v-bind="propsObj"
        class="header__access-link header__access-link--wide"
        label="Get Account Access"
    />
</template>
