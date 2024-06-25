<script>
import { inject } from "vue";
import { useRoute } from "vue-router";

import _isEmpty from "lodash/isEmpty";

import { formatDate } from "utilities/filters";
import {
    getCurrentPageResultsRange,
    getFileTypeButton,
    DOCUMENT_TYPES_MAP,
} from "utilities/utils";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import DivisionLabel from "sharedComponents/results-item-parts/DivisionLabel.vue";
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
    if (item.resource.type === "internal") {
        linkText = item.document_name_headline || item.resource.document_id;
    } else {
        linkText = item.summary_headline || item.summary_string;
    }

    return `<span class='result__link--label'>${linkText}</span>`;
};

const showResultSnippet = (item) => {
    if (
        item.resource.type === "internal_file" &&
        (item.content_headline || item.summary_headline || item.summary_string)
    )
        return true;

    if (item.resource.type === "public_link" && item.content_headline) return true;

    return false;
};

const getResultSnippet = (item) => {
    let snippet;

    if (item.resource.type === "internal_file") {
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

    if (item.resource.type === "public_link") {
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
const props = defineProps({
    results: {
        type: Array,
        default: () => [],
    },
    resultsCount: {
        type: Number,
        default: 0,
    },
    page: {
        type: String,
        default: "1",
    },
    pageSize: {
        type: Number,
        default: 10,
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
    view: {
        type: String,
        default: undefined,
    },
});

const $route = useRoute();

const apiUrl = inject("apiUrl");
const base = inject("base");

const getUrl = ({ type: resourceType, url, uid }) =>
    resourceType === "public_link" ? url : `${apiUrl}resources/internal/files/${uid}`;

const needsBar = (item) =>
    item.resource.type === "public_link" &&
    item.resource.date &&
    item.resource.document_id;

const resultLinkClasses = (doc) => ({
    external: doc.resource.type === "public_link",
    "document__link--search": !!$route?.query?.q,
});

const currentPageResultsRange = getCurrentPageResultsRange({
    count: props.resultsCount,
    page: props.page,
    pageSize: props.pageSize,
});
</script>

<template>
    <div class="doc__list">
        <template v-if="view !== 'search'">
            <h2 v-if="searchQuery" class="search-results__heading">
                Search Results
            </h2>
            <div class="search-results-count">
                <span v-if="results.length > 0"
                    >{{ currentPageResultsRange[0] }} -
                    {{ currentPageResultsRange[1] }} of</span
                >
                {{ resultsCount }} <span v-if="searchQuery">result</span
                ><span v-else>document</span>
                <span v-if="results.length != 1">s</span>
                <span v-if="searchQuery">
                    for
                    <span class="search-query__span">{{
                        searchQuery
                    }}</span></span
                >
                <span v-if="searchQuery && selectedSubjectParts[0]">
                    within {{ selectedSubjectParts[1][0] }}</span
                >
            </div>
        </template>
        <slot name="empty-state"></slot>
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
                    v-if="!_isEmpty(doc.resource.type)"
                    :icon-type="doc.resource.type"
                    :doc-type="DOCUMENT_TYPES_MAP[doc.resource.type]"
                />
                <template v-if="doc.resource.type === 'internal_file'">
                    <CategoryLabel
                        v-if="!_isEmpty(doc.resource.category)"
                        :name="
                            doc.category?.parent
                                ? doc.resource?.category?.parent?.name
                                : doc.resource?.category?.name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="doc.resource?.category?.parent"
                        :name="doc.resource?.category?.name"
                        type="subcategory"
                    />
                </template>
                <template v-else>
                    <CategoryLabel
                        v-if="!_isEmpty(doc.resource.category)"
                        :name="
                            doc.category?.parent
                                ? doc.resource?.category?.parent?.name
                                : doc.resource?.category?.name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="doc.resource?.category?.parent"
                        :name="doc.resource?.category?.name"
                        type="subcategory"
                    />
                </template>
            </template>
            <template #context>
                <span
                    v-if="doc.resource.date"
                    class="result__context--date"
                    :class="needsBar(doc) && 'result__context--date--bar'"
                    >{{ formatDate(doc.resource.date) }}</span
                >
                <!-- DivisionLabel
                    v-if="doc.type === 'internal' && doc.division"
                    :division="doc.division"
                /-->
                <span
                    v-if="
                        doc.resource.type === 'public_link' && doc.resource.document_id
                    "
                    >{{ doc.resource.document_id }}</span
                >
            </template>
            <template #link>
                <a
                    :href="getUrl(doc.resource)"
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
                    v-if="doc.resource.subjects.length > 0"
                    class="document__info-block"
                >
                    <SubjectChips :subjects="doc.resource.subjects" />
                </div>
            </template>
            <template #sections>
                <RelatedSections
                    :base="base"
                    :item="doc.resource"
                    :parts-last-updated="partsLastUpdated"
                    label="Related Regulation Citation"
                />
            </template>
        </ResultsItem>
    </div>
</template>
