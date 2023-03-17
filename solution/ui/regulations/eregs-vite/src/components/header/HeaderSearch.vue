<script setup>
import { computed, ref } from "vue";

import HeaderSearchIcon from "../svgs/header-search-icon.vue";
import HeaderLeftChevron from "../svgs/header-left-chevron.vue";

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

const expandStateClasses = computed(() => ({
    hidden: !mobileSearchExpanded.value,
    visible: mobileSearchExpanded.value,
}));
</script>

<template>
    <form class="search__form" :action="searchUrl">
        <button
            type="button"
            class="form__button--close-mobile-search"
            aria-label="Close Search Bar"
            @click="expandSearchClick"
        >
            <template v-if="mobileSearchExpanded">
                <HeaderLeftChevron />
            </template>
            <template v-else>
                <HeaderSearchIcon />
            </template>
        </button>
        <input
            :class="expandStateClasses"
            type="search"
            name="q"
            placeholder="Search"
        />
        <button
            type="submit"
            class="search__button--submit"
            :class="expandStateClasses"
            aria-label="Search"
        >
            <i class="fa fa-search"></i>
            <HeaderSearchIcon />
        </button>
    </form>
</template>
