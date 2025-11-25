<script>
import { computed, inject } from "vue";
import { useRoute } from "vue-router";

import isEmpty from "lodash/isEmpty";

import { formatDate } from "utilities/filters";
import {
    createRegResultLink,
    deserializeResult,
    getCurrentPageResultsRange,
    getFileNameSuffix,
    getFileTypeButton,
    getFrDocType,
    getLinkDomainFileTypeEl,
    getLinkDomainString,
    hasRegulationCitations,
    hasStatuteCitations,
    DOCUMENT_TYPES_MAP,
} from "utilities/utils";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";
import IndicatorLabel from "sharedComponents/results-item-parts/IndicatorLabel.vue";
import RelatedSectionsCollapse from "sharedComponents/results-item-parts/RelatedSectionsCollapse.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";

import SubjectChips from "./SubjectChips.vue";

const addSurroundingEllipses = (str) => {
    if (!str) return "";

    if (str.includes("search-highlight")) return `...${str}...`;

    return str;
};

const getParentCategoryName = ({ itemCategory, categoriesArr }) => {
    if (!itemCategory) return null;

    const parentId = itemCategory.parent;

    if (!parentId) return null;

    const parentCategory = categoriesArr.find(
        (category) => category.id == parentId
    );

    return parentCategory?.name ?? null;
};

const getResultLinkText = (item) => {
    const fileName = item.type === "internal_file"
        ? item.file_name
        : item.url;

    let linkText;
    if (DOCUMENT_TYPES_MAP[item.type] === "Internal") {
        linkText = item.name_headline || item.title;
    } else {
        linkText =
            item.summary_headline ||
            item.name_headline ||
            item.summary_string ||
            item.node_title ||
            item.title;
    }

    const fileTypeButton = getFileTypeButton({
        fileName,
        uid: item.uid,
    });

    const domainString = getLinkDomainString({ url: item.url, className: "result__link--domain" });
    const domainFileTypeEl = getLinkDomainFileTypeEl(
        linkText,
        domainString,
        fileTypeButton
    );

    return `<span class='result__link--label'>${domainFileTypeEl}</span>`;
};

const showResultSnippet = (item) => {
    if (
        DOCUMENT_TYPES_MAP[item.type] === "Internal" &&
        (item.content_headline ||
            item.summary_headline ||
            item.summary_string ||
            item.summary)
    )
        return true;

    if (DOCUMENT_TYPES_MAP[item.type] === "Public" && item.content_headline)
        return true;

    return false;
};

const getResultSnippet = (item) => {
    let snippet;

    if (DOCUMENT_TYPES_MAP[item.type] === "Internal") {
        if (
            item.content_headline &&
            item.content_headline.includes("search-highlight")
        ) {
            snippet = addSurroundingEllipses(item.content_headline);
        } else if (item.summary_headline) {
            snippet = addSurroundingEllipses(item.summary_headline);
        } else if (item.summary_string) {
            snippet = item.summary_string;
        } else if (item.summary) {
            snippet = item.summary;
        }

        return snippet;
    }

    if (DOCUMENT_TYPES_MAP[item.type] === "Public") {
        if (item.content_headline) {
            snippet = addSurroundingEllipses(item.content_headline);
        } else if (item.content_string) {
            snippet = item.content_string;
        }
    }

    return snippet;
};

const partDocumentTitleLabel = (string) => string.toLowerCase();

export default {
    addSurroundingEllipses,
    getParentCategoryName,
    getResultLinkText,
    getResultSnippet,
    partDocumentTitleLabel,
    showResultSnippet,
};
</script>

<script setup>
const props = defineProps({
    categories: {
        type: Array,
        default: () => [],
    },
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
});

const $route = useRoute();

const apiUrl = inject("apiUrl");
const homeUrl = inject("homeUrl");

const transformedResults = computed(() =>
    props.results.map((result) => deserializeResult(result))
);

const getUrl = (doc) =>
    doc.type === "internal_file"
        ? `${apiUrl}resources/internal/files/${doc.uid}`
        : doc.type === "reg_text"
            ? createRegResultLink(
                {
                    date: doc.date,
                    headline: doc.content_headline,
                    part_number: doc.part_number,
                    section_number: doc.node_id,
                    section_title: doc.title,
                    title: doc.reg_title,
                },
                homeUrl,
                $route.query?.q
            )
            : doc.url;

const needsBar = (item) => item.date && item.document_id;

const resultLinkClasses = (doc) => ({
    "document__link--search": !!$route?.query?.q,
    "document__link--regulations": doc.type === "reg_text",
    "document__link--internal-file": doc.file_name && DOCUMENT_TYPES_MAP[doc.type] === "Internal",
});

const currentPageResultsRange = getCurrentPageResultsRange({
    count: props.resultsCount,
    page: props.page,
    pageSize: props.pageSize,
});
</script>

<template>
    <div class="doc__list">
        <div class="search-results-count">
            <div class="count__info-row">
                <div class="count__info">
                    <span v-if="results.length > 0">{{ currentPageResultsRange[0] }} -
                        {{ currentPageResultsRange[1] }} of</span>
                    {{ resultsCount }} <span v-if="searchQuery">result</span><span v-else>document</span>
                    <span v-if="results.length != 1">s</span>
                </div>
            </div>
            <slot name="sign-in-cta" />
        </div>
        <slot name="empty-state" />
        <ResultsItem
            v-for="doc in transformedResults"
            :key="doc.uid"
            class="doc-list__document"
        >
            <template #actions>
                <a
                    v-if="hasEditableJobCode && doc.id"
                    class="edit-button"
                    :href="`${apiUrl}resources/${doc.id}/edit`"
                >
                    Edit
                    <i class="fas fa-edit" />
                </a>
            </template>
            <template #labels>
                <DocTypeLabel
                    v-if="doc.type"
                    :icon-type="doc.type"
                    :doc-type="DOCUMENT_TYPES_MAP[doc.type]"
                />
                <CategoryLabel
                    v-if="doc.type === 'reg_text'"
                    name="Regulations"
                    type="regulations"
                />
                <CategoryLabel
                    v-else-if="!isEmpty(doc.category)"
                    :name="
                        doc.category?.parent
                            ? getParentCategoryName({
                                itemCategory: doc.category,
                                categoriesArr: categories,
                            })
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
            <template #context>
                <IndicatorLabel
                    v-if="
                        doc.category?.is_fr_link_category && getFrDocType(doc)
                    "
                    :type="getFrDocType(doc)"
                />
                <template v-if="doc.part_title || doc.subpart_title">
                    <span
                        v-if="doc.part_title"
                        class="result__context--date"
                        data-testid="part-title"
                    >{{
                        partDocumentTitleLabel(doc.part_title)
                    }}</span>
                    <span
                        v-if="doc.subpart_title"
                        class="result__context--division result__context--division--bar"
                        data-testid="subpart-bar"
                    />
                    <span
                        v-if="doc.subpart_title"
                        class="result__context--division"
                        data-testid="subpart-title"
                    >
                        {{ doc.subpart_title }}
                    </span>
                </template>
                <span
                    v-else-if="doc.date"
                    class="result__context--date"
                    :class="needsBar(doc) && 'result__context--date--bar'"
                >{{ formatDate(doc.date) }}</span>
                <span v-if="doc.document_id">{{ doc.document_id }}</span>
            </template>
            <template #link>
                <a
                    v-sanitize-html="getResultLinkText(doc)"
                    :data-file-name="doc.file_name ? doc.file_name : null"
                    :data-file-extension="doc.file_name ? getFileNameSuffix(doc.file_name) : null"
                    :href="getUrl(doc)"
                    :target="doc.type === 'reg_text' ? undefined : '_blank'"
                    :rel="
                        doc.type === 'reg_text'
                            ? undefined
                            : 'noopener noreferrer'
                    "
                    class="document__link document__link--filename"
                    :class="resultLinkClasses(doc)"
                />
            </template>
            <template #snippet>
                <div
                    v-if="showResultSnippet(doc)"
                    v-sanitize-html="getResultSnippet(doc)"
                />
            </template>
            <template #chips>
                <div
                    v-if="doc.subjects?.length > 0"
                    class="document__info-block"
                >
                    <SubjectChips :subjects="doc.subjects" />
                </div>
            </template>
            <template #sections>
                <RelatedSectionsCollapse
                    v-if="
                        doc.type !== 'reg_text' &&
                            (hasRegulationCitations({ doc, partsLastUpdated })
                                || hasStatuteCitations({ doc }))"
                    :item="doc"
                    :parts-last-updated="partsLastUpdated"
                    :has-statute-citations="hasStatuteCitations({ doc })"
                    :has-regulation-citations="hasRegulationCitations({ doc, partsLastUpdated })"
                />
            </template>
        </ResultsItem>
    </div>
</template>
