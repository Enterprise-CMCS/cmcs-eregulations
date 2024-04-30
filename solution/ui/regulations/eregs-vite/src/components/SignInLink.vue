<script setup>
import { useRoute } from "vue-router";
import useLoginRedirectUrl from "composables/login";

const props = defineProps({
    customLoginUrl: {
        type: String,
        required: true,
    },
    homeUrl: {
        type: Object,
        required: true,
    },
    isAuthenticated: {
        type: Boolean,
        required: true,
    },
    linkLabel: {
        type: String,
        default: "sign in",
    },
});

const $route = useRoute();

const loginUrl = useLoginRedirectUrl({
    customLoginUrl: props.customLoginUrl,
    homeUrl: props.homeUrl,
    route: $route,
});
</script>

<template>
    <a :href="loginUrl" rel="noopener noreferrer">{{ linkLabel }}</a>
</template>

<style></style>
