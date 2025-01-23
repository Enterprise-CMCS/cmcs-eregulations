<script setup>
const props = defineProps({
    accessUrl: {
        type: String,
        required: true,
    },
    isAuthenticated: {
        type: Boolean,
        required: true,
    },
    testId: {
        type: String,
        default: "loginSpa",
    },
});
</script>

<template>
    <div class="div__login-cta">
        <span :data-testid="testId"
            >To see internal documents,
            <slot name="sign-in-link">sign in</slot></span
        >
        or
        <a :href="accessUrl">learn how to get account access</a>.
    </div>
</template>
