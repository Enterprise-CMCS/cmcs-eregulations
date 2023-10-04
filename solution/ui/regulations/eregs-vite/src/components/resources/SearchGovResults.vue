<script setup>
import { formatDate } from "utilities/filters";

import RelatedSections from "@/components/search/RelatedSections.vue";

import Label from "sharedComponents/results-item-parts/Label.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
    results: {
        type: Array,
        default: () => [],
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
});

const openChar = ""; // &#xe000;
const closeChar = ""; // &#xe001;
const highlightClass = "search-highlight";

const needsBar = (item) => item.date && item.name;

/**
 * @param string {string} - string containing substrings surrounded by special characters
 * @param startChar {string} - character that indicates the start of a substring to get
 * @param stopChar {string} - character that indicates the end of a substring to get
 * @returns {Array{string}} - Array of unique substrings
 */
const getHighlightTerms = (string, startChar, stopChar) => {
    // pure fns for composition
    const splitString = (str, splitChar) => str.split(splitChar);
    const getFirstItem = (arr) => arr.shift();
    const removeFirstItem = (arr) => {
        getFirstItem(arr);
        return arr;
    };
    const mapFn = (fn, arr, args = []) => arr.map((item) => fn(item, ...args));
    const uniqArr = (arr) => Array.from(new Set(arr));

    return uniqArr(
        mapFn(
            getFirstItem,
            mapFn(
                splitString,
                removeFirstItem(splitString(string, startChar)),
                [stopChar]
            )
        )
    );
};

/**
 * https://jsdoc.app/tags-param.html -- see "Documenting a destructuring parameter"
 *
 * @param supplementalContentItem {Object} - A piece of supplemental content
 * @param supplementalContentItem.description {?string} - description of the piece of supplemental content
 * @param supplementalContentItem.description_headline {?string} - alternate description of the piece of supplemental content.  Usually null
 * @param supplementalContentItem.snippet {?string} - snippet of descriptive text containing special characters that are surrounding substrings to be emphasized with bold styles
 * @param startChar {string} - character that indicates the start of a substring to highlight
 * @param stopChar {string} - character that indicates the end of a substring to highlight
 * @returns {string} - description with opening and closing span tags surrounding substrings that are to be emphasized
 */
const formatLinkTitle = (
    { description, description_headline, snippet },
    startChar,
    stopChar
) => {
    let linkTitle = description_headline || description;

    if (!snippet) {
        return linkTitle;
    }

    const termsToHighlight = getHighlightTerms(snippet, startChar, stopChar);

    termsToHighlight.forEach((term) => {
        linkTitle = linkTitle.replaceAll(
            term,
            `<span class="${highlightClass}">${term}</span>`
        );
    });

    return linkTitle;
};

/**
 * @param snippet {?string} - snippet of descriptive text containing special characters that are surrounding substrings to be emphasized with bold styles
 * @param startChar {string} - character that indicates the start of a substring to highlight
 * @param stopChar {string} - character that indicates the end of a substring to highlight
 * @returns {string} - snippet with special characters replaced with opening and closing span tags with a class used to add highlighting styles
 */
const formatSnippet = (snippet, startChar, stopChar) => {
    if (!snippet) {
        return snippet;
    }

    const reOpen = new RegExp(startChar, "g");
    const reClose = new RegExp(stopChar, "g");

    return snippet
        .replace(reOpen, `<span class="${highlightClass}">`)
        .replace(reClose, "</span>");
};
</script>

<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
        <template v-for="(item, idx) in results">
            <ResultsItem :key="item.created_at + idx">
                <template #labels>
                    <Label
                        :name="
                            item.category.parent
                                ? item.category.parent.name
                                : item.category.name
                        "
                        type="category"
                    />
                    <Label
                        v-if="item.category.parent"
                        :name="item.category.name"
                        type="subcategory"
                    />
                </template>
                <template #context>
                    <span
                        v-if="item.date"
                        class="result__context--date"
                        :class="needsBar(item) && 'result__context--date--bar'"
                        >{{ formatDate(item.date) }}</span
                    >
                    <span v-if="item.name">{{ item.name }}</span>
                </template>
                <template #link>
                    <a
                        :href="item.url"
                        target="_blank"
                        rel="noopener noreferrer"
                        v-html="formatLinkTitle(item, openChar, closeChar)"
                        class="external"
                    >
                    </a>
                </template>
                <template #snippet>
                    <div
                        v-html="
                            formatSnippet(item.snippet, openChar, closeChar)
                        "
                    />
                </template>
                <template #sections>
                    <RelatedSections
                        :base="base"
                        :item="item"
                        :parts-last-updated="partsLastUpdated"
                    />
                </template>
            </ResultsItem>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>
