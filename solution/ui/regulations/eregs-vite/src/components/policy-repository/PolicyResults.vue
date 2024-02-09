<script>
import { inject } from "vue";
import { useRoute } from "vue-router/composables";

import _isEmpty from "lodash/isEmpty";

import { formatDate } from "utilities/filters";
import { getFileTypeButton, DOCUMENT_TYPES_MAP } from "utilities/utils";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";
import RelatedSections from "sharedComponents/results-item-parts/RelatedSections.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";

import SubjectChips from "./SubjectChips.vue";

const addSurroundingEllipses = (str) => {
    if (!str) return "";

    if (str.includes("search-highlight")) return `...${str}...`;

    return str;
};

const getResultLinkText = (item) => {
    let linkText;
    if (item.resource_type === "internal") {
        linkText = item.document_name_headline || item.doc_name_string;
    } else {
        linkText = item.summary_headline || item.summary_string;
    }

    return `<span class='result__link--label'>${linkText}</span>`;
};

const showResultSnippet = (item) => {
    if (
        item.resource_type === "internal" &&
        (item.content_headline || item.summary_headline || item.summary_string)
    )
        return true;

    if (item.resource_type === "external" && item.content_headline) return true;

    return false;
};

const getResultSnippet = (item) => {
    let snippet;

    if (item.resource_type === "internal") {
        if (
            item.content_headline &&
            item.content_headline.includes("search-highlight")
        ) {
            snippet = addSurroundingEllipses(item.content_headline);
        } else if (item.summary_headline) {
            snippet = addSurroundingEllipses(item.summary_headline);
        } else if (item.summary_string) {
            snippet = item.summary_string;
        }

        return snippet;
    }

    if (item.resource_type === "external") {
        if (item.content_headline) {
            snippet = addSurroundingEllipses(item.content_headline);
        } else if (item.content_string) {
            snippet = item.content_string;
        }
    }

    return snippet;
};

export default {
    addSurroundingEllipses,
    getResultLinkText,
    getResultSnippet,
    showResultSnippet,
};
</script>

<script setup>
defineProps({
    results: {
        type: Array,
        default: () => [],
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
    hasEditableJobCode: {
        type: Boolean,
        default: false,
    },
    searchQuery: {
        type: String,
        default: "",
    },
    selectedSubjectParts: {
        type: Array,
        default: () => [],
    },
});

const $route = useRoute();

const apiUrl = inject("apiUrl");
const base = inject("base");

const getUrl = ({ resource_type: resourceType, url }) =>
    resourceType === "external" ? url : `${apiUrl}file-manager/files/${url}`;

const needsBar = (item) =>
    item.resource_type === "external" &&
    item.date_string &&
    item.doc_name_string;

const resultLinkClasses = (doc) => ({
    external: doc.resource_type === "external",
    "document__link--search": !!$route?.query?.q,
});
</script>

<template>
    <div class="doc__list">
        <h2 v-if="searchQuery" class="search-results__heading">
            Search Results
        </h2>
        <div class="search-results-count">
            <span v-if="results.length > 0">1 - {{ results.length }} of</span>
            {{ results.length }} <span v-if="searchQuery">result</span
            ><span v-else>document</span>
            <span v-if="results.length != 1">s</span>
            <span v-if="searchQuery">
                for
                <span class="search-query__span">{{ searchQuery }}</span></span
            >
            <span v-if="searchQuery && selectedSubjectParts[0]">
                within {{ selectedSubjectParts[1][0] }}</span
            >
        </div>
        <ResultsItem
            v-for="doc in results"
            :key="doc.uid"
            class="doc-list__document"
        >
            <template #actions>
                <a
                    v-if="hasEditableJobCode"
                    class="edit-button"
                    :href="apiUrl + 'content-search/resource/' + doc.id"
                >
                    Edit
                    <i class="fas fa-edit"></i>
                </a>
            </template>
            <template #labels>
                <DocTypeLabel
                    v-if="!_isEmpty(doc.resource_type)"
                    :icon-type="doc.resource_type"
                    :doc-type="DOCUMENT_TYPES_MAP[doc.resource_type]"
                />
                <template v-if="doc.resource_type === 'internal'">
                    <CategoryLabel
                        v-if="!_isEmpty(doc.category)"
                        :name="
                            doc.category?.parent
                                ? doc.category?.parent?.name
                                : doc.category?.name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="doc.category?.parent"
                        :name="doc.category?.name"
                        type="subcategory"
                    />
                </template>
                <template v-else>
                    <CategoryLabel
                        v-if="!_isEmpty(doc.category)"
                        :name="
                            doc.category?.parent
                                ? doc.category?.parent?.name
                                : doc.category?.name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="doc.category?.parent"
                        :name="doc.category?.name"
                        type="subcategory"
                    />
                </template>
            </template>
            <template #context>
                <span
                    v-if="doc.date_string"
                    class="result__context--date"
                    :class="needsBar(doc) && 'result__context--date--bar'"
                    >{{ formatDate(doc.date_string) }}</span
                >
                <span
                    v-if="
                        doc.resource_type === 'external' && doc.doc_name_string
                    "
                    >{{ doc.doc_name_string }}</span
                >
            </template>
            <template #link>
                <a
                    :href="getUrl(doc)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="document__link document__link--filename"
                    :class="resultLinkClasses(doc)"
                    v-html="
                        getResultLinkText(doc) +
                        getFileTypeButton({
                            fileName: doc.file_name_string,
                            url: doc.url,
                        })
                    "
                ></a>
            </template>
            <template #snippet>
                <div
                    v-if="showResultSnippet(doc)"
                    v-html="getResultSnippet(doc)"
                />
            </template>
            <template #chips>
                <div
                    v-if="doc.subjects.length > 0"
                    class="document__info-block"
                >
                    <SubjectChips :subjects="doc.subjects" />
                </div>
            </template>
            <template #sections>
                <RelatedSections
                    :base="base"
                    :item="doc"
                    :parts-last-updated="partsLastUpdated"
                    label="Related Regulation Citation"
                />
            </template>
        </ResultsItem>
    </div>
</template>

<style></style>
