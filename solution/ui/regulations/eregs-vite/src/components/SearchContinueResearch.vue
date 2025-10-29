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
    `https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=${encodeURIComponent(
        query
    )}`;

const makeMedicaidGovLink = (query) =>
    `https://www.medicaid.gov/search/content?keys=${encodeURIComponent(query)}`;

const makeUsCodeLink = (query) => {
    const urlEncodedQuery = encodeURIComponent(query);

    let base64Query;
    try {
        base64Query = btoa(query);
    } catch (_error) {
        base64Query = "";
    }

    const urlEncodedBase64Query = encodeURIComponent(base64Query);

    return `https://uscode.house.gov/search.xhtml?edition=prelim&searchString=%28${urlEncodedQuery}%29+AND+%28%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2819%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2821%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2818%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2816%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2811%29%29%29&pageNumber=1&itemsPerPage=100&sortField=RELEVANCE&displayType=CONTEXT&action=search&q=${urlEncodedBase64Query}%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7Ctrue%7C%5B42%3A%3A%3A%3A7%3A19%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A21%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A18%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A16%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A11%3A%3A%3Atrue%3A%5D%7C%5BQWxsIEZpZWxkcw%3D%3D%3A%5D`;
};

export default {
    hasQuotes,
    hasSpaces,
    makeEcfrLink,
    makeFederalRegisterLink,
    makeMedicaidGovLink,
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

// TODO: truncate very long queries for display

const containerClasses = computed(() => ({
    "more-info__container--results": props.resultsCount > 0,
    "more-info__container--no-results": props.resultsCount == 0,
}));

const hasActiveFilters = computed(() => props.activeFilters.length > 0);
</script>

<template>
    <div class="more-info__container" :class="containerClasses">
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
                >"{{ stripQuotes(query) }}"</router-link>
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
        <div class="more-info__row" data-testid="research-row-2">
            <span class="row__title">Try your search for <strong>{{ query }}</strong> on other
                websites</span>
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
