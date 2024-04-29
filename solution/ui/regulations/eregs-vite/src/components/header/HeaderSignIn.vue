<script setup>
import { useRoute } from "vue-router";
import { useRouterLogin, useWindowLogin } from "composables/login";

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
});

const $route = useRoute();

const loginUrl = useRouterLogin({
    customLoginUrl: props.customLoginUrl,
    homeUrl: props.homeUrl,
    route: $route,
});
</script>

<template>
    <div class="skeleton">
        <a :href="loginUrl" rel="noopener noreferrer">Sign In</a>
    </div>
</template>

<style></style>
