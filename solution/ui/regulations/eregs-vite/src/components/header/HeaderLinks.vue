<script setup>
import { ref } from "vue";

import HeaderChevronUp from "../svgs/header-chevron-up.vue";
import HeaderChevronDown from "../svgs/header-chevron-down.vue";

const props = defineProps({
    aboutUrl: {
        type: String,
        required: true,
    },
    resourcesUrl: {
        type: String,
        required: true,
    },
});

const links = [
    {
        name: "resources",
        label: "Resources",
        active: window.location.pathname.includes("resources"),
        href: props.resourcesUrl,
    },
    {
        name: "about",
        label: "About",
        active: window.location.pathname.includes("about"),
        href: props.aboutUrl,
    },
];

const moreMenuExpanded = ref(false);

const moreClick = () => {
    moreMenuExpanded.value = !moreMenuExpanded.value;
};

const closeClick = () => {
    moreMenuExpanded.value = false;
};
</script>

<template>
    <div class="links--container">
        <ul class="links__list links__list--wide">
            <li v-for="(link, index) in links" :key="index">
                <a
                    class="header--links__anchor"
                    :class="{ active: link.active }"
                    :href="link.href"
                >
                    <span class="anchor__span">{{ link.label }}</span>
                </a>
            </li>
        </ul>
        <button class="more__button" @click="moreClick">
            <HeaderChevronUp v-show="moreMenuExpanded" />
            <HeaderChevronDown v-show="!moreMenuExpanded" />
            <span>More</span>
        </button>
        <div
            v-show="moreMenuExpanded"
            v-clickaway="closeClick"
            class="more--dropdown-menu"
        >
            <ul class="links__list links__list--dropdown">
                <li v-for="(link, index) in links" :key="index">
                    <a
                        class="header--links__anchor"
                        :class="{ active: link.active }"
                        :href="link.href"
                    >
                        <span class="anchor__span">{{ link.label }}</span>
                    </a>
                </li>
            </ul>
        </div>
    </div>
</template>
