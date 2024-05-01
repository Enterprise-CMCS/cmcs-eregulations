<script setup>
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
    route: {
        type: Object,
        default: undefined,
    },
});

const loginUrl = useLoginRedirectUrl({
    customLoginUrl: props.customLoginUrl,
    homeUrl: props.homeUrl,
    route: props.route,
});
</script>

<template>
    <a :href="loginUrl" rel="noopener noreferrer">{{ linkLabel }}</a>
</template>

<style></style>
