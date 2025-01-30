<script setup>
const props = defineProps({
    accessUrl: {
        type: String,
        required: true,
    },
    testId: {
        type: String,
        default: "loginSpa",
    },
});
</script>

<template>
    <div class="login-cta__div">
        <span :data-testid="testId">To see internal documents,
            <slot name="sign-in-link">sign in</slot></span>
        or
        <a
            class="access__anchor"
            :href="accessUrl"
        >learn how to get account access</a>.
    </div>
</template>
