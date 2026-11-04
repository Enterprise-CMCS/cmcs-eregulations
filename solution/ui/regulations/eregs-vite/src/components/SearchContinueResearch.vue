<script>
import { computed } from "vue";

import {
    stripQuotes,
    truncateQueryForDisplay,
} from "utilities/utils";

const hasSpaces = (str) => /[\s]/.test(str);
const hasQuotes = (str) => /["']/.test(str);

const makeEcfrLink = ({ query, title }) =>
    `https://www.ecfr.gov/search?search[hierarchy][title]=${title}&search[query]=${encodeURIComponent(
        query
    )}`;

const makeFederalRegisterLink = (query) =>
    `https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=${encodeURIComponent(
        query
    )}`;

const makeMedicaidGovLink = (query) =>
    `https://www.medicaid.gov/search/content?keys=${encodeURIComponent(query)}`;

export default {
    hasQuotes,
    hasSpaces,
    makeEcfrLink,
    makeFederalRegisterLink,
    makeMedicaidGovLink,
};
</script>

<script setup>
import {
    SEARCH_STRING_TRUNCATE_THRESHOLD,
} from "utilities/utils";

const props = defineProps({
    query: {
        type: String,
        required: false,
        default: "",
    },
    resultsCount: {
        type: Number,
        default: 0,
    },
    parent: {
        type: String,
        default: "search",
    },
    activeFilters: {
        type: Array,
        default: () => [],
    },
});

const containerClasses = computed(() => ({
    "more-info__container--results": props.resultsCount > 0,
    "more-info__container--no-results": props.resultsCount == 0,
}));

const hasActiveFilters = computed(() => props.activeFilters.length > 0);

const truncatedQuery = computed(() => truncateQueryForDisplay({ query: props.query }));
</script>

<template>
    <div
        v-if="query && query.length <= SEARCH_STRING_TRUNCATE_THRESHOLD"
        class="more-info__container"
        :class="containerClasses"
    >
        <h3 class="more-info__title">
            Continue Your Research
        </h3>
        <div
            v-if="resultsCount > 0 && !hasQuotes(query) && hasSpaces(query)"
            class="more-info__row"
            data-testid="research-row-1"
        >
            <span class="row__title">Make your search more specific</span>
            <span class="row__content" data-testid="quoted-search-link-parent">
                Try your search with quotes:
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
                >"{{ truncatedQuery }}"</router-link>
            </span>
        </div>
        <div
            v-else-if="hasActiveFilters"
            class="more-info__row"
            data-testid="research-row-1"
        >
            <span class="row__title">Broaden your search on eRegulations</span>
            <span class="row__content" data-testid="reset-filters-parent">
                Choose a different filter option above or
                <router-link
                    :to="{
                        name: parent,
                        query: {
                            q: query,
                        },
                    }"
                >
                    reset all active filters</router-link>.
            </span>
        </div>
        <div
            class="more-info__row"
            data-testid="research-row-2"
        >
            <span class="row__title">Try your search for <strong>{{ truncatedQuery }}</strong> on other websites</span>
            <ul class="row__content row__content--list">
                <li>
                    <a
                        :href="makeEcfrLink({ query, title: 42 })"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >eCFR Title 42</a>
                </li>
                <li>
                    <a
                        :href="makeEcfrLink({ query, title: 45 })"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >eCFR Title 45</a>
                </li>
                <li>
                    <a
                        :href="makeMedicaidGovLink(query)"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >Medicaid.gov</a>
                </li>
                <li>
                    <a
                        :href="makeFederalRegisterLink(query)"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >Federal Register</a>
                </li>
            </ul>
        </div>
    </div>
</template>
