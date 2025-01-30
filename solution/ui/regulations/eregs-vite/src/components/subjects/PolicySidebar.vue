<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";
import useLoginRedirectUrl from "composables/login";

const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");

const $route = useRoute();

const loginUrl = useLoginRedirectUrl({
    customLoginUrl,
    homeUrl,
    route: $route,
});
</script>

<template>
    <div class="sidebar__filters">
        <slot name="title">
            <h2>Research a Subject</h2>
        </slot>
        <div class="sidebar-filters__container">
            <slot name="filters" />
        </div>
    </div>
</template>
