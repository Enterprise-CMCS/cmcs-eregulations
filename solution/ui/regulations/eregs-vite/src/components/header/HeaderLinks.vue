<script setup>
import useDropdownMenu from "composables/dropdownMenu";

import HeaderChevronUp from "../svgs/header-chevron-up.vue";
import HeaderChevronDown from "../svgs/header-chevron-down.vue";
import HeaderDropdownMenu from "./HeaderDropdownMenu.vue";
import HeaderLink from "./HeaderLink.vue";

const props = defineProps({
    statutesUrl: {
        type: String,
        required: true,
    },
    subjectsUrl: {
        type: String,
        required: true,
    },
});

defineEmits(["link-clicked"]);

const links = [
    {
        name: "statutes",
        label: "Access Statute Citations",
        active: window.location.pathname.includes("statutes"),
        href: props.statutesUrl,
    },
    {
        name: "subjects",
        label: "Research a Subject",
        active: window.location.pathname.includes("subjects"),
        href: props.subjectsUrl,
    },
];

const { menuExpanded, toggleClick, closeClick } = useDropdownMenu();
</script>

<template>
    <div class="links--container">
        <ul class="links__list links__list--wide">
            <li v-for="(link, index) in links" :key="index">
                <HeaderLink
                    v-bind="link"
                    @click="$emit(`link-clicked`, link.name)"
                />
            </li>
        </ul>
        <button class="more__button" @click="toggleClick">
            <HeaderChevronUp v-show="menuExpanded" />
            <HeaderChevronDown v-show="!menuExpanded" />
            <span>More</span>
        </button>
        <HeaderDropdownMenu
            v-if="menuExpanded"
            class="more--dropdown-menu"
            @close-menu="closeClick"
        >
            <template #dropdown-menu-content>
                <ul class="links__list links__list--dropdown">
                    <li v-for="(link, index) in links" :key="index">
                        <HeaderLink v-bind="link" />
                    </li>
                </ul>
            </template>
        </HeaderDropdownMenu>
    </div>
</template>
