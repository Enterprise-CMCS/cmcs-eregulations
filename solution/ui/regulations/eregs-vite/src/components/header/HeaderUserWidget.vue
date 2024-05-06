<script setup>
import useDropdownMenu from "composables/dropdownMenu";

import HeaderDropdownMenu from "./HeaderDropdownMenu.vue";
import UserIconSvg from "../svgs/user-icon.vue";

const props = defineProps({
    username: {
        type: String,
        default: "User",
    },
});

const { menuExpanded, toggleClick, closeClick } = useDropdownMenu();

const formLogout = () => {
    document.oidc_logout.submit();
};
</script>

<template>
    <button class="user-account__button" @click="toggleClick">
        <UserIconSvg />
    </button>
    <HeaderDropdownMenu
        v-if="menuExpanded"
        class="dropdown-menu--account"
        @close-menu="closeClick"
    >
        <template #dropdown-menu-content>
            <div class="account-info">
                <strong>
                    <slot name="username">
                        {{ props.username }}
                    </slot>
                </strong>
                <div class="account-message">
                    While signed in, you can access documents
                    <strong>internal to CMCS</strong>.
                </div>
                <slot name="user-account-content"></slot>
            </div>
            <hr>
            <slot name="sign-out-link">
                <button class="sign-out__button" @click="formLogout">Vue Sign Out</button>
            </slot>
        </template>
    </HeaderDropdownMenu>
</template>

<style></style>
