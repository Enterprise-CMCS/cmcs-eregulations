<template>
    <div class="result">
        <div class="results-part">
            {{ result.part_document_title | partDocumentTitleLabel }}
        </div>
        <div class="results-section">
            <a
                :href="createResultLink(result, base)"
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
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        removeQuotes(string) {
            return stripQuotes(string);
        },
        createResultLink(result, base) {
            // get highlight content from result.headline
            const highlightedTerms = getTagContent(
                result.headline,
                "search-highlight"
            );
            const highlightParams = highlightedTerms
                ? `?q=${highlightedTerms}`
                : "";
            return `${base}/${result.part_title}/${result.label[0]}/${
                result.label[1]
            }/${result.date}/${highlightParams}#${result.label.join("-")}`;
        },
    },

    filters: {
        partDocumentTitleLabel(string) {
            return string.toLowerCase();
        }
    },
};
</script>

<style>
.results-part {
    text-transform: capitalize;
}
</style>
