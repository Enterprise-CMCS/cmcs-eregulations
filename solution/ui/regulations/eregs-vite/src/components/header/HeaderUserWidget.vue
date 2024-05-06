<script setup>
import { computed } from "vue";

import useDropdownMenu from "composables/dropdownMenu";

import HeaderDropdownMenu from "./HeaderDropdownMenu.vue";
import UserIconSvg from "../svgs/user-icon.vue";

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
    <button :class="iconClasses" @click="toggleClick">
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
                        <slot name="username"></slot>
                    </strong>
                </div>
                <div class="account-info--msg">
                    <div class="account-message">
                        While signed in, you can access documents
                        <strong>internal to CMCS</strong>.
                    </div>
                    <slot name="user-account-content"></slot>
                </div>
            </div>
            <hr />
            <slot name="sign-out-link">
                <button class="sign-out__button" @click="formLogout">
                    Vue Sign Out
                </button>
            </slot>
        </template>
    </HeaderDropdownMenu>
</template>

<style></style>
