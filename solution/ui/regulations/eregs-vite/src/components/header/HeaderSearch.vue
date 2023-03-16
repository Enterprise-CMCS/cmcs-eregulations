<script setup>
defineProps({
    searchUrl: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <form class="search__form" :action="searchUrl">
        <input type="search" name="q" placeholder="Search" />
        <button
            type="submit"
            class="search__button--submit"
            aria-label="Search"
        >
            <i class="fa fa-search"></i>
        </button>
    </form>
</template>
