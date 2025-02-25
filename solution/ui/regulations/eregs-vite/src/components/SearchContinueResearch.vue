<script>
import { computed } from "vue";

import { stripQuotes } from "utilities/utils";

const hasSpaces = (str) => /[\s]/.test(str);
const hasQuotes = (str) => /["']/.test(str);

const makeEcfrLink = ({ query, title }) =>
    `https://www.ecfr.gov/search?search[hierarchy][title]=${title}&search[query]=${encodeURIComponent(
        query
    )}`;

const makeFederalRegisterLink = (query) =>
    `https://www.federalregister.gov/documents/search?conditions[agencies][]=&conditions[term]=${encodeURIComponent(
        query
    )}`;

const makeGovSiteLink = (query) =>
    `https://www.opm.gov/search#${encodeURIComponent(
        query
    )}`;

const makeUsCodeLink = (query) => {
    const urlEncodedQuery = encodeURIComponent(query);
    const base64Query = btoa(query);
    const urlEncodedBase64Query = encodeURIComponent(base64Query);

    return `https://uscode.house.gov/search.xhtml?edition=prelim&searchString=${urlEncodedQuery}&pageNumber=1&itemsPerPage=100&sortField=RELEVANCE&displayType=CONTEXT&action=search&q=${urlEncodedBase64Query}%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7Cfalse%7C%5B%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%5D%7C%5B%3A%5D`;
};

export default {
    hasQuotes,
    hasSpaces,
    makeEcfrLink,
    makeFederalRegisterLink,
    makeGovSiteLink,
    makeUsCodeLink,
};
</script>

<script setup>
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
    "research__container--results": props.resultsCount > 0,
    "research__container--no-results": props.resultsCount == 0,
}));

const hasActiveFilters = computed(() => props.activeFilters.length > 0);
</script>

<template>
    <div class="research__container" :class="containerClasses">
        <h3 class="research__title">
            Continue Your Research
        </h3>
        <div
            v-if="resultsCount > 0 && !hasQuotes(query) && hasSpaces(query)"
            class="research__row"
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
                >"{{ stripQuotes(query) }}"</router-link>
            </span>
        </div>
        <div
            v-else-if="hasActiveFilters"
            class="research__row"
            data-testid="research-row-1"
        >
            <span class="row__title">Broaden your search</span>
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
        <div class="research__row" data-testid="research-row-2">
            <span class="row__title">Try your search for <strong>{{ query }}</strong> on other
                websites</span>
            <ul class="row__content row__content--list">
                <li>
                    <a
                        :href="makeEcfrLink({ query, title: 5 })"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >eCFR Title 5</a>
                </li>
                <li>
                    <a
                        :href="makeGovSiteLink(query)"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >OPM.gov</a>
                </li>
                <li>
                    <a
                        :href="makeFederalRegisterLink(query)"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >Federal Register</a>
                </li>
                <li>
                    <a
                        :href="makeUsCodeLink(query)"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                    >United States Code</a>
                </li>
            </ul>
        </div>
    </div>
</template>
