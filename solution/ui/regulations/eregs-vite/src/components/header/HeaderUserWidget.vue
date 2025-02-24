<script setup>
import { computed } from "vue";

import useDropdownMenu from "composables/dropdownMenu";

import HeaderDropdownMenu from "./HeaderDropdownMenu.vue";
import UserIconSvg from "../svgs/user-icon.vue";

defineProps({
    adminUrl: {
        type: String,
        default: "/admin/",
    },
});

const { menuExpanded, toggleClick, closeClick } = useDropdownMenu();

const formLogout = () => {
    document.oidc_logout.submit();
};

const iconClasses = computed(() => ({
    "user-account__button": true,
    "user-account__button--expanded": menuExpanded.value,
}));
</script>

<template>
    <button
        aria-label="Account Information"
        :class="iconClasses"
        data-testid="user-account-button"
        @click="toggleClick"
    >
        <UserIconSvg />
    </button>
    <HeaderDropdownMenu
        v-if="menuExpanded"
        class="dropdown-menu--account"
        @close-menu="closeClick"
    >
        <template #dropdown-menu-content>
            <div class="account-info__container">
                <div class="account-info--username">
                    <strong>
                        <slot name="username" />
                    </strong>
                </div>
                <div class="account-info--msg">
                    <div class="account-message">
                    </div>
                </div>
                <div class="account-info--links">
                    <a
                        :href="adminUrl"
                        rel="noopener noreferrer"
                        data-testid="manage-content-link"
                    >Manage Content</a>
                </div>
            </div>
            <hr>
            <div class="account--sign-out">
                <slot name="sign-out-link">
                    <button
                        class="sign-out__button"
                        data-testid="vue-sign-out-button"
                        @click="formLogout"
                    >
                        Sign Out
                    </button>
                </slot>
            </div>
        </template>
    </HeaderDropdownMenu>
</template>

<style></style>
