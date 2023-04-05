<script setup>
import {
    formatDate,
    locationLabel,
    locationUrl,
} from "../../utilities/filters";

import ResultsItem from "@/components/search/ResultsItem.vue";
import SupplementalContentObject from "eregsComponentLib/src/components/SupplementalContentObject.vue";

defineProps({
    base: {
        type: String,
        required: true,
    },
    partsLastUpdated: {
        type: Object,
        required: true,
    },
    partsList: {
        type: Array,
        required: true,
    },
    results: {
        type: Array,
        default: () => [],
    },
});

const openChar = ""; // &#xe000;
const closeChar = ""; // &#xe001;
const highlightClass = "search-highlight";

const needsBar = (item) => item.date && item.name;

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

const formatLinkTitle = ({ description, descriptionHeadline, snippet }) => {
    const termsToHighlight = getHighlightTerms(snippet, openChar, closeChar);

    let linkTitle = descriptionHeadline || description;
    termsToHighlight.forEach((term) => {
        linkTitle = linkTitle.replaceAll(
            term,
            `<span class="${highlightClass}">${term}</span>`
        );
    });

    return linkTitle;
};

const formatSnippet = (snippet) => {
    const reOpen = new RegExp(openChar, "g");
    const reClose = new RegExp(closeChar, "g");

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
                    <div class="category-labels">
                        <div class="result-label category-label">
                            {{
                                item.category.parent
                                    ? item.category.parent.name
                                    : item.category.name
                            }}
                        </div>
                        <div
                            v-if="item.category.parent"
                            class="result-label subcategory-label"
                        >
                            {{ item.category.name }}
                        </div>
                    </div>
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
                        v-html="formatLinkTitle(item)"
                        class="external"
                    >
                    </a>
                </template>
                <template #snippet>
                    <div v-html="formatSnippet(item.snippet)" />
                </template>
                <template #sections>
                    <div class="related-sections">
                        <span class="related-sections-title">
                            Related Section<span
                                v-if="item.locations.length > 1"
                                >s</span
                            >:
                        </span>
                        <span v-if="item.locations.length > 1">§§ </span>
                        <span v-else>§ </span>
                        <template v-for="(location, i) in item.locations">
                            <span
                                :key="location.display_name + i"
                                class="related-section-link"
                            >
                                <a
                                    :href="
                                        locationUrl(
                                            location,
                                            partsList,
                                            partsLastUpdated,
                                            base
                                        )
                                    "
                                >
                                    {{ locationLabel(location) }}
                                </a>
                                <span v-if="i + 1 != item.locations.length">
                                    |
                                </span>
                            </span>
                        </template>
                    </div>
                </template>
            </ResultsItem>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>
