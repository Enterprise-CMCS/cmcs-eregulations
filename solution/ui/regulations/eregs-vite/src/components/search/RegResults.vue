<script setup>
import { getTagContent, stripQuotes } from "@/utilities/utils";

import ResultsItem from "@/components/search/ResultsItem.vue";

defineProps({
    base: {
        type: String,
        required: true,
    },
    results: {
        type: Array,
        default: () => [],
    },
    query: {
        type: String,
        default: "",
    },
});

const partDocumentTitleLabel = (string) => string.toLowerCase();

const removeQuotes = (string) => stripQuotes(string);
const createResultLink = (
    { headline, title, part_number, section_number, date, section_title },
    base,
    query
) => {
    // get highlight content from headline
    const highlightedTermsArray = getTagContent(headline, "search-highlight");
    let q = query.replace("%", "%25")
    const uniqTermsArray = Array.from(
        new Set([q, ...highlightedTermsArray])
    );

    const highlightParams =
        uniqTermsArray.length > 0 ? `?q=${uniqTermsArray.join(",")}` : "";

    let section = section_number
    let location = `${part_number}-${section_number}`

    if (section_title.includes("Appendix")){
        section = `Subpart-${section}`
        location = `${section_title.split('-')[0].trim().replace(/\s/g,"-")}`
    }

    return `${base}${title}/${part_number}/${section}/${date}/${highlightParams}#${location}`;
};
</script>

<template>
    <div class="reg-results-container">
        <slot name="empty-state"></slot>
        <template v-for="(result, i) in results">
            <ResultsItem :key="i">
                <template #context>
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

<style></style>
