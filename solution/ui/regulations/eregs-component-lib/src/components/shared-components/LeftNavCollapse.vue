<script setup>
import { computed, getCurrentInstance, onMounted, onUnmounted, ref } from "vue";

const props = defineProps({
    contentsDescription: {
        type: String,
        required: false,
        default: "menu",
    },
});

// replace placeholder nav on mounted to maintain formatting/spacing
onMounted(() => {
    // getCurrentInstance works with Vue2,
    // but will need to use template refs when upgrading to Vue3
    const { $rootNav } = getCurrentInstance().proxy.$refs;

    const placeholderNav = document.getElementById("placeholderNav");

    placeholderNav.replaceWith($rootNav);
});

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
const explicitOpen = ref(windowWidth.value >= 1024);
const responsiveOpen = computed(() => windowWidth.value >= 1024);

const userHasClicked = ref(false);

// If user has toggled sidebar open or closed, use that value
// Otherwise, use responsive value
const navOpen = computed(() => {
    if (userHasClicked.value) {
        return explicitOpen.value;
    }

    return responsiveOpen.value;
});

const toggleClick = () => {
    if (userHasClicked.value === false) {
        userHasClicked.value = true;

        explicitOpen.value = !responsiveOpen.value;
    } else {
        explicitOpen.value = !explicitOpen.value;
    }
};

const navClasses = computed(() => ({
    open: navOpen.value,
    closed: !navOpen.value,
}));

// set button icon based on navOpen
const btnIcon = computed(() => (navOpen.value ? "mdi-close" : "mdi-menu"));

const btnClasses = computed(() => ({
    "full-btn": navOpen.value === true,
    "icon-only": navOpen.value === false,
}));

const btnAriaLabel = computed(() =>
    navOpen.value
        ? `Close ${props.contentsDescription}`
        : `Open ${props.contentsDescription}`
);
</script>

<template>
    <nav
        id="leftNav"
        ref="$rootNav"
        class="toc__nav"
        :class="navClasses"
    >
        <v-btn
            class="nav-toggle__button"
            :class="btnClasses"
            :ripple="false"
            :icon="navOpen"
            :aria-label="btnAriaLabel"
            variant="text"
            @click="toggleClick"
            @mouseenter="hoverOn"
            @mouseleave="hoverOff"
            @focus="toggleFocus"
            @blur="toggleFocus"
        >
            <v-icon class="nav-toggle__button--icon" :class="btnHoverClasses">
                {{
                    btnIcon
                }}
            </v-icon>
            <span v-if="!navOpen" class="nav-toggle__button--label">Menu</span>
        </v-btn>
        <div v-show="navOpen">
            <slot name="nav-contents" />
        </div>
    </nav>
</template>
