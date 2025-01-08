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
</script>

<template>
    <HeaderLink
        name="get-account-access"
        label="Get Account Access"
        :active="isActive"
        :href="getAccessUrl"
    />
</template>
