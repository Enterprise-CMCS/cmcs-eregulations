<script setup>
import { computed, ref } from "vue";

// Nav open or closed
const navOpen = ref(true);

const toggleClick = () => {
    navOpen.value = !navOpen.value;
};

const btnIcon = computed(() => (navOpen.value ? "mdi-close" : "mdi-menu"));

const btnClasses = computed(() => ({
    "full-btn": navOpen.value === true,
    "icon-only": navOpen.value === false,
}));

const navClasses = computed(() => ({
    open: navOpen.value,
    closed: !navOpen.value,
}));

const btnHovered = ref(false);
const btnFocused = ref(false);

// Open/close toggle btn hovered or focused

const toggleHover = () => {
    btnHovered.value = !btnHovered.value;
};

const toggleFocus = () => {
    btnFocused.value = !btnFocused.value;
};

const btnHoverClasses = computed(() => ({
    "nav-toggle__button--hovered": btnHovered.value || btnFocused.value,
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
            :class="btnClasses"
            :ripple="false"
            :x-small="!navOpen"
            :icon="navOpen"
            outlined
            plain
            @click="toggleClick"
            @mouseenter="toggleHover"
            @mouseleave="toggleHover"
            @focus="toggleFocus"
            @blur="toggleFocus"
        >
            <v-icon class="nav-toggle__button--icon" :class="btnHoverClasses">{{
                btnIcon
            }}</v-icon>
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
