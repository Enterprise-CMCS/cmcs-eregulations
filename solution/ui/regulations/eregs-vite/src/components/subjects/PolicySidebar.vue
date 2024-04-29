<script setup>
import { inject, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useRouterLogin, useWindowLogin } from "composables/login";

const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");

const $route = useRoute();

const loginUrl = useRouterLogin({ customLoginUrl, homeUrl, route: $route });

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
