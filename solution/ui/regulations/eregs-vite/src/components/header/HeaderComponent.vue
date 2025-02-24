<script setup>
defineProps({
    homeUrl: {
        type: String,
        required: true,
    },
});

const isLoginPage = window.location.pathname.includes("login");
</script>

<template>
    <div class="header--content-container">
        <div class="header__row header__row--first">
            <div class="header--brand">
                <a :href="homeUrl">Policy <br>Connector</a>
            </div>
            <div class="header--search">
                <slot name="search" />
            </div>
            <div class="header--sign-in" :class="{ active: isLoginPage }">
                <slot name="sign-in" />
            </div>
            <slot name="get-access" />
        </div>
        <div class="header__row header__row--second">
            <div class="header--jump-to">
                <slot name="jump-to" />
            </div>
            <div class="header--links">
                <slot name="links" />
            </div>
        </div>
    </div>
</template>
