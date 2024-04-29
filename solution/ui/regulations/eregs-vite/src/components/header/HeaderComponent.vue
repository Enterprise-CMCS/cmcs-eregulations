<script setup>
defineProps({
    homeUrl: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="header--content-container">
        <div class="header__row header__row--first">
            <div class="header--brand">
                <a :href="homeUrl">Medicaid &amp; <br/>CHIP eRegulations</a>
            </div>
            <div class="header--search">
                <slot name="search"></slot>
            </div>
            <div class="header--sign-in">
                <slot name="sign-in"></slot>
            </div>
        </div>
        <div class="header__row header__row--second">
            <div class="header--jump-to">
                <slot name="jump-to"></slot>
            </div>
            <div class="header--links">
                <slot name="links"></slot>
            </div>
        </div>
    </div>
</template>
