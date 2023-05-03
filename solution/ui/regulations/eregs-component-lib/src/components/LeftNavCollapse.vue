<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";

// Watch window width
const windowWidth = ref(window.innerWidth);

const onWidthChange = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => window.addEventListener("resize", onWidthChange));
onUnmounted(() => window.removeEventListener("resize", onWidthChange));

// Open/close toggle btn hovered or focused
const btnHovered = ref(false);
const btnFocused = ref(false);

const hoverOn = () => {
    btnHovered.value = true;
};

const hoverOff = () => {
    btnHovered.value = false;
};

const toggleFocus = () => {
    btnFocused.value = !btnFocused.value;
};

const btnHoverClasses = computed(() => ({
    "nav-toggle__button--hovered": btnHovered.value || btnFocused.value,
}));

// Nav open or closed to start
const navOpen = ref(windowWidth.value >= 1024);
const responsiveOpen = computed(() => (windowWidth.value >= 1024));

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
            @mouseenter="hoverOn"
            @mouseleave="hoverOff"
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

<style></style>
