<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";

defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const $route = useRoute();
</script>

<template>
    <div class="subj-landing__container">
    <p>TBD</p>
    </div>
</template>

<style></style>
