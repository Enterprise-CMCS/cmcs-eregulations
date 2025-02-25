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
    active: isActive,
    href: getAccessUrl.value,
};
</script>

<template>
    <HeaderLink
        v-bind="propsObj"
        name="get-account-access-narrow"
        class="header__access-link header__access-link--narrow"
        label="Placeholder"
    />
    <HeaderLink
        v-bind="propsObj"
        name="get-account-access-wide"
        class="header__access-link header__access-link--wide"
        label="Placeholder"
    />
</template>
