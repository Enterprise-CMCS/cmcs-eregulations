<script setup>
import { computed, ref } from "vue";

// open or closed
const navOpen = ref(true);

const toggleClick = () => {
    navOpen.value = !navOpen.value;
};

const btnIcon = computed(() => (navOpen.value ? "mdi-close" : "mdi-menu"));

const navClasses = computed(() => ({
    open: navOpen.value,
    closed: !navOpen.value,
}));
// Russian doll, slots all the way down
// This component is specifically for left nav with open/close abilities
// Column that collapses/expands horizontally for wide widths. Will have a max width
// Column that collapses/expands vertically from top for narrow widths.  Will be full width
// this component will:
// 1. open and close
// 2. have a max width (prop?)
</script>

<template>
    <nav id="leftNav" :class="navClasses">
        <v-btn
            class="nav-toggle__button"
            :class="toggleBtnClasses"
            :ripple="false"
            :x-small="!navOpen"
            :icon="navOpen"
            outlined
            @click="toggleClick"
        >
            <v-icon class="nav-toggle__button--icon">{{ btnIcon }}</v-icon>
            <span v-if="!navOpen" class="nav-toggle__button--label">Menu</span>
        </v-btn>
        <template v-if="navOpen">
            <slot></slot>
        </template>
    </nav>
</template>

<style lang="scss">
nav#leftNav {
    &.open {
        width: 400px;
    }

    &.closed {
        width: 75px;
    }
}
</style>
