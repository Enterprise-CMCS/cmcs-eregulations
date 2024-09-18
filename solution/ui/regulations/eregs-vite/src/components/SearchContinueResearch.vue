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
});

const containerClasses = computed(() => ({
    "research__container--no-results": props.resultsCount === 0,
}));

const eregsLink = computed(() =>
    props.query ? `${this.eregs_url}?q=${this.query}` : this.eregs_url
);

const ecfrLink = computed(
    () =>
        `https://www.ecfr.gov/search?search[hierarchy][title]=42&search[query]=${this.query}`
);

const federalRegisterLink = computed(
    () =>
        `https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=${this.query}`
);

const medicaidGovLink = computed(
    () =>
        `https://www.medicaid.gov/search-gsc?&gsc.sort=#gsc.tab=0&gsc.q=${this.query}&gsc.sort=`
);

const unitedStatesCodeLink = computed(
    () =>
        `https://uscode.house.gov/search.xhtml?edition=prelim&searchString=%28${this.query}+%28title%3A42+chapter%3A7+subchapter%3A19%29+OR+%28title%3A42+chapter%3A7+subchapter%3A21%29+%29&pageNumber=1&itemsPerPage=100&sortField=RELEVANCE&displayType=CONTEXT&action=search&q=dGVzdCAodGl0bGU6NDIgY2hhcHRlcjo3IHN1YmNoYXB0ZXI6MTkpIE9SICh0aXRsZTo0MiBjaGFwdGVyOjcgc3ViY2hhcHRlcjoyMSkg%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7Ctrue%7C%5B%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%5D%7C%5BQWxsIEZpZWxkcw%3D%3D%3A%3BQWxsIEZpZWxkcw%3D%3D%3A%5D`
);
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
                    >Try your search with quotes around it: "{{
                        query
                    }}"</span
                >
                <span v-else
                    >Choose a different filter option above or reset all active
                    filters.</span
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
