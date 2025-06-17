<script setup>
defineProps({
    accessUrl: {
        type: String,
        required: true,
    },
    desiredActionString: {
        type: String,
        default: "see internal documents",
    },
    testId: {
        type: String,
        default: "loginSpa",
    },
});
</script>

<template>
    <div class="login-cta__div">
        <span :data-testid="testId">To {{ desiredActionString }},
            <slot name="sign-in-link">sign in</slot></span>
        or
        <a
            class="access__anchor"
            :href="accessUrl"
        >learn how to get account access</a>.
    </div>
</template>
