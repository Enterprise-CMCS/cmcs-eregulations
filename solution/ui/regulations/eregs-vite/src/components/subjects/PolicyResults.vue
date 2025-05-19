<script>
import { computed, inject } from "vue";
import { useRoute } from "vue-router";

import isEmpty from "lodash/isEmpty";

import { formatDate } from "utilities/filters";
import {
    createRegResultLink,
    deserializeResult,
    getCurrentPageResultsRange,
    getFileTypeButton,
    getFrDocType,
    DOCUMENT_TYPES_MAP,
} from "utilities/utils";

import CollapseButton from "eregsComponentLib/src/components/CollapseButton.vue";
import Collapsible from "eregsComponentLib/src/components/Collapsible.vue";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";
import IndicatorLabel from "sharedComponents/results-item-parts/IndicatorLabel.vue";
import RelatedSections from "sharedComponents/results-item-parts/RelatedSections.vue";
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

    return `<span class='result__link--label'>${linkText}</span>${fileTypeButton}`;
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

const getCollapseName = (doc) =>
    `related citations collapsible ${doc.id ?? doc.node_id}`;

const hasRegulationCitations = ({ doc, partsLastUpdated }) => {
    const regCitations = doc.cfr_citations
        ? doc.cfr_citations.filter((location) => {
            const { part } = location;
            return partsLastUpdated[part];
        })
        : [];

    return regCitations.length > 0;
};

/**
 * Checks if the document has statute citations.
 *
 * @param {Object} doc - The document object.
 * @param {Array} doc.act_citations - Array of act citations.
 * @param {Array} doc.usc_citations - Array of USC citations.
 * @returns {boolean} - Returns true if the document has both statute citation fields in the response and if one of those fields has a length > 0, false otherwise.
 */
const hasStatuteCitations = ({ doc }) => {
    // ensure that both act_citations and usc_citations fields are present
    if (!doc.act_citations || !doc.usc_citations) return false;

    // if both fields exist, check if either field has citations
    return doc.act_citations.length > 0 || doc.usc_citations.length > 0;
};

export default {
    addSurroundingEllipses,
    getParentCategoryName,
    getResultLinkText,
    getResultSnippet,
    partDocumentTitleLabel,
    showResultSnippet,
    getCollapseName,
    hasRegulationCitations,
    hasStatuteCitations,
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
    external:
        doc.type !== "reg_text" &&
        (doc.type === "internal_link" ||
            DOCUMENT_TYPES_MAP[doc.type] === "Public"),
    "document__link--search": !!$route?.query?.q,
    "document__link--regulations": doc.type === "reg_text",
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
                <span v-if="doc.part_title" class="result__context--date">{{
                    partDocumentTitleLabel(doc.part_title)
                }}</span>
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
                <CollapseButton
                    v-if="
                        doc.type !== 'reg_text' &&
                            (hasRegulationCitations({ doc, partsLastUpdated })
                                || hasStatuteCitations({ doc }))"
                    :name="getCollapseName(doc)"
                    state="collapsed"
                    class="related-citations__btn--collapse"
                >
                    <template #expanded>
                        Hide Related Citations
                        <i class="fa fa-chevron-up" />
                    </template>
                    <template #collapsed>
                        Show Related Citations
                        <i class="fa fa-chevron-down" />
                    </template>
                </CollapseButton>
                <Collapsible
                    :name="getCollapseName(doc)"
                    state="collapsed"
                    class="collapse-content"
                    overflow
                >
                    <template v-if="doc.type !== 'reg_text'">
                        <RelatedSections
                            v-if="hasStatuteCitations({ doc })"
                            :base="homeUrl"
                            :item="doc"
                            label="Statutes"
                        />
                        <RelatedSections
                            v-if="hasRegulationCitations({ doc, partsLastUpdated })"
                            :base="homeUrl"
                            :item="doc"
                            :parts-last-updated="partsLastUpdated"
                            label="Regulations"
                        />
                    </template>
                </Collapsible>
            </template>
        </ResultsItem>
    </div>
</template>
