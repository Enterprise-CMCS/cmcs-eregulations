<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";

import SignInCTA from "@/components/SignInCTA.vue";
import SignInLink from "@/components/SignInLink.vue";

const aboutUrl = inject("aboutUrl");
const accessUrl = inject("accessUrl");
const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");

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

    </div>
</template>

<style></style>
