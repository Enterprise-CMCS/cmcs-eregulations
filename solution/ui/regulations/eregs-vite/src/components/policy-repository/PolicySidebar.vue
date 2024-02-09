<script setup>
import { inject, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router/composables";

const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");

const $route = useRoute();

const loginUrl = ref(customLoginUrl);

const setLoginUrl = () => {
    if (!$route.fullPath.includes("?")) {
        loginUrl.value = customLoginUrl;
        return;
    }

    const pathQuery = $route.fullPath.split("?")[1];

    if (pathQuery.length == 0) {
        loginUrl.value = customLoginUrl;
        return;
    }

    loginUrl.value = `${customLoginUrl}?next=${homeUrl}policy-repository/?${pathQuery}`;
};

watch(
    () => $route.query,
    async (newQueryParams) => {
        setLoginUrl();
    }
);

setLoginUrl();
</script>

<template>
    <div class="sidebar__filters">
        <slot name="title">
            <h2>Find Policy Documents</h2>
        </slot>
        <div class="sidebar-filters__container">
            <slot name="selections"> </slot>
            <slot name="search"> </slot>
            <template v-if="!isAuthenticated">
                <div class="div__login-sidebar">
                    CMCS staff participating in the Policy Repository pilot can
                    <a :href="loginUrl" rel="noopener noreferrer">sign in</a>
                    to see internal resources.
                </div>
            </template>
            <slot name="filters"></slot>
        </div>
    </div>
</template>
