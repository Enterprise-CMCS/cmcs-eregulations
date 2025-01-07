<script setup>
import HeaderLink from "./header/HeaderLink.vue";

defineProps({
    href: {
        type: String,
        required: true,
    },
});

const isActive = window.location.pathname.includes("get-account-access");
</script>

<template>
    <HeaderLink
        name="get-account-access"
        label="Get Account Access"
        :active="isActive"
        :href="href"
    />
</template>
