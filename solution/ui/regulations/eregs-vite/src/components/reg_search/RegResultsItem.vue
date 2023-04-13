<template>
    <div class="result">
        <div class="results-part">
            {{ result.part_title | partDocumentTitleLabel }}
        </div>
        <div class="results-section">
            <a
                :href="createResultLink(result, base, query)"
                v-html="removeQuotes(result.parentHeadline)"
            />
        </div>
        <div class="results-preview" v-html="result.headline" />
    </div>
</template>

<script>
import { getTagContent, stripQuotes } from "@/utilities/utils";

export default {
    name: "RegResultsItem",

    components: {},

    props: {
        base: {
            type: String,
            required: true,
        },
        result: {
            type: Object,
            required: true,
        },
        query: {
            type: String,
            default: "",
        },
    },

    methods: {
        removeQuotes(string) {
            return stripQuotes(string);
        },
        createResultLink(result, base, query) {
            // get highlight content from result.headline
            const highlightedTermsArray = getTagContent(
                result.headline,
                "search-highlight"
            );

            const uniqTermsArray = Array.from(
                new Set([query, ...highlightedTermsArray])
            );

            let section = result.section_number
            let location = `${result.part_number}-${result.section_number}`

            if (result.section_title.includes("Appendix")){
                section = `Subpart-${result.section_number}`
                location = `${result.section_title.split('-')[0].trim().replace(/\s/g,"-")}`
            }
            const highlightParams =
                uniqTermsArray.length > 0
                    ? `?q=${uniqTermsArray.join(",")}`
                    : "";

            return `${base}${result.title}/${result.part_number}/${section}/${result.date}/${highlightParams}#${location}`;
        },
    },

    filters: {
        partDocumentTitleLabel(string) {
            return string.toLowerCase();
        },
    },
};
</script>

<style>
.results-part {
    text-transform: capitalize;
}
</style>
