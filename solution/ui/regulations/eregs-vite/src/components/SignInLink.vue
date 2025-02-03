<script setup>
import { computed } from "vue";
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
    location: {
        type: String,
        default: undefined,
    },
    directLink: {
        type: String,
        default: undefined,
    },
});

const loginUrl = useLoginRedirectUrl({
    customLoginUrl: props.customLoginUrl,
    homeUrl: props.homeUrl,
    route: props.route,
    directLink: props.directLink,
});

const linkClasses = computed(() => ({
    disabled: props.location === "login_page",
}));
</script>

<template>
    <template v-if="location === 'login_page'">
        <span class="disabled">{{ linkLabel }}</span>
    </template>
    <template v-else>
        <a
            :href="loginUrl"
            :class="linkClasses"
            rel="noopener noreferrer"
        >{{
            linkLabel
        }}</a>
    </template>
</template>

<style></style>
