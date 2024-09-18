<script setup>
import { computed } from "vue";

import { stripQuotes } from "utilities/utils";

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
    sanitizedQueryParams: {
        type: Object,
        default: () => [],
    },
});

const containerClasses = computed(() => ({
    "research__container--results": props.resultsCount > 0,
    "research__container--no-results": props.resultsCount == 0,
}));

const activeFilters = computed(() =>
    props.sanitizedQueryParams.filter(([key, _value]) => key !== "q")
);

const hasActiveFilters = computed(() => activeFilters.value.length > 0);
</script>

<template>
    <div class="research__container" :class="containerClasses">
        <div class="research__title">Continue Your Research</div>
        <div v-if="resultsCount > 0 || hasActiveFilters" class="research__row">
            <span class="row__title">{{
                resultsCount > 0
                    ? "Make your search more specific"
                    : "Broaden your search on eRegulations"
            }}</span>
            <span class="row__content">
                <span v-if="resultsCount > 0"
                    >Try your search with quotes:
                    <router-link
                        :to="{
                            name: parent,
                            query: {
                                ...activeFilters.reduce(
                                    (acc, [key, value]) => ({
                                        ...acc,
                                        [key]: value,
                                    }),
                                    {}
                                ),
                                q: `&quot;${stripQuotes(query)}&quot;`,
                            },
                        }"
                        >"{{ stripQuotes(query) }}"</router-link
                    >
                </span>
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
