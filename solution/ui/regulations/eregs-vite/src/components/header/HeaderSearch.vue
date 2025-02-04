<script setup>
import { computed, ref } from "vue";

import HeaderSearchIcon from "../svgs/header-search-icon.vue";
import HeaderChevronLeft from "../svgs/header-chevron-left.vue";

defineProps({
    searchUrl: {
        type: String,
        required: true,
    },
});

const mobileSearchExpanded = ref(false);

const expandSearchClick = () => {
    mobileSearchExpanded.value = !mobileSearchExpanded.value;
};

const formClasses = computed(() => ({
    "search__form--expanded": mobileSearchExpanded.value,
}));

const expandStateClasses = computed(() => ({
    hidden: !mobileSearchExpanded.value,
    "visible--mobile": mobileSearchExpanded.value,
}));

const expandButtonAriaLabel = computed(
    () => `${mobileSearchExpanded.value ? "Hide" : "Show"} search bar`
);
</script>

<template>
    <form
        class="search__form"
        :class="formClasses"
        :action="searchUrl"
    >
        <button
            type="button"
            class="form__button--toggle-mobile-search"
            :aria-label="expandButtonAriaLabel"
            @click="expandSearchClick"
        >
            <HeaderChevronLeft v-show="mobileSearchExpanded" />
            <HeaderSearchIcon v-show="!mobileSearchExpanded" />
        </button>
        <input
            :class="expandStateClasses"
            type="search"
            name="q"
            placeholder="Search"
        >
        <button
            type="submit"
            class="search__button--submit"
            :class="expandStateClasses"
            aria-label="Search"
        >
            <i class="fa fa-search" />
            <HeaderSearchIcon />
        </button>
    </form>
</template>
