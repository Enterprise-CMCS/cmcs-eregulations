<script setup>
import { inject } from "vue";

import { getTagContent, stripQuotes } from "utilities/utils";

import ResultsItem from "sharedComponents/ResultsItem.vue";

defineProps({
    results: {
        type: Array,
        default: () => [],
    },
    query: {
        type: String,
        default: "",
    },
});

const base = inject("base");

const partDocumentTitleLabel = (string) => string.toLowerCase();

const removeQuotes = (string) => stripQuotes(string);
const createResultLink = (
    { headline, title, part_number, section_number, date, section_title },
    baseUrl,
    query
) => {
    // get highlight content from headline
    const highlightedTermsArray = getTagContent(headline, "search-highlight");
    const rawQuery = query.replace("%", "%25");
    const uniqTermsArray = Array.from(
        new Set([rawQuery, ...highlightedTermsArray])
    );

    const highlightParams =
        uniqTermsArray.length > 0 ? `?q=${uniqTermsArray.join(",")}` : "";

    let section = section_number;
    let location = `${part_number}-${section_number}`;

    if (section_title.includes("Appendix")) {
        section = `Subpart-${section}`;
        location = `${section_title.split("-")[0].trim().replace(/\s/g, "-")}`;
    }

    return `${baseUrl}${title}/${part_number}/${section}/${date}/${highlightParams}#${location}`;
};
</script>

<template>
    <div class="reg-results-container">
        <slot name="empty-state"></slot>
        <template v-for="(result, i) in results" :key="i">
            <ResultsItem>
                <template #context>
                    {{ result.title }} CFR
                    {{ partDocumentTitleLabel(result.part_title) }}
                </template>
                <template #link>
                    <a
                        :href="createResultLink(result, base, query)"
                        v-html="removeQuotes(result.parentHeadline)"
                    />
                </template>
                <template #snippet>
                    <div v-html="result.headline" />
                </template>
            </ResultsItem>
        </template>
    </div>
</template>
