<script setup>
import { computed } from "vue";

const props = defineProps({
    query: {
        type: String,
        required: false,
    },
    resultsCount: {
        type: Number,
        default: 0,
    },
    parent: {
        type: String,
        default: "search",
    },
});

const containerClasses = computed(() => ({
    "research__container--results": props.resultsCount > 0,
    "research__container--no-results": props.resultsCount == 0,
}));
</script>

<template>
    <div class="research__container" :class="containerClasses">
        <div class="research__title">Continue Your Research</div>
        <div class="research__row">
            <span class="row__title">{{
                searchResults > 0
                    ? "Make your search more specific"
                    : "Broaden your search on eRegulations"
            }}</span>
            <span class="row__content">
                <span v-if="searchResults > 0"
                    >Try your search with quotes around it: "{{ query }}"</span
                >
                <span v-else
                    >Choose a different filter option above or
                    <router-link
                        :to="{
                            name: parent,
                            query: {
                                q: query,
                            },
                        }"
                    >
                        reset all active filters</router-link
                    >.</span
                >
            </span>
        </div>
        <div class="research__row">
            <span class="row__title"
                >Try your search for <strong>{{ query }}</strong> on other
                websites</span
            >
            <span class="row__content">List of website links here</span>
        </div>
    </div>
</template>
