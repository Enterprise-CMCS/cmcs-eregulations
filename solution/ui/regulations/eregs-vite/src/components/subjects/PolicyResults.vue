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

const getFieldVal = ({ item, fieldName }) => {
    if (item?.resource) {
        return item.resource[fieldName];
    } else if (item?.reg_text) {
        return item.reg_text[fieldName];
    } else {
        return item[fieldName];
    }
};

const getParentCategoryName = ({ item, categoriesArr }) => {
    if (!item) return null;

    const parentId = getFieldVal({ item, fieldName: "category" }).parent;

    if (!parentId) return null;

    const parentCategory = categoriesArr.find(
        (category) => category.id === parentId
    );

    return parentCategory?.name ?? null;
};

const getResultLinkText = (item) => {
    let linkText;
    if (
        DOCUMENT_TYPES_MAP[getFieldVal({ item, fieldName: "type" })] ===
        "Internal"
    ) {
        linkText =
            item.name_headline || getFieldVal({ item, fieldName: "title" });
    } else {
        linkText =
            item.summary_headline ||
            item.name_headline ||
            item.summary_string ||
            getFieldVal({ item, fieldName: "node_title" }) ||
            getFieldVal({ item, fieldName: "title" });
    }

    return `<span class='result__link--label'>${linkText}</span>`;
};

const showResultSnippet = (item) => {
    if (
        DOCUMENT_TYPES_MAP[getFieldVal({ item, fieldName: "type" })] ===
            "Internal" &&
        (item.content_headline ||
            item.summary_headline ||
            item.summary_string ||
            item.summary)
    )
        return true;

    if (
        DOCUMENT_TYPES_MAP[getFieldVal({ item, fieldName: "type" })] ===
            "Public" &&
        item.content_headline
    )
        return true;

    return false;
};

const getResultSnippet = (item) => {
    let snippet;

    if (
        DOCUMENT_TYPES_MAP[getFieldVal({ item, fieldName: "type" })] ===
        "Internal"
    ) {
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

    if (
        DOCUMENT_TYPES_MAP[getFieldVal({ item, fieldName: "type" })] ===
        "Public"
    ) {
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
    view: {
        type: String,
        default: undefined,
    },
});

const $route = useRoute();

const apiUrl = inject("apiUrl");
const base = inject("base");

const getUrl = ({ type: resourceType, url, uid }) =>
    resourceType === "internal_file"
        ? `${apiUrl}resources/internal/files/${uid}`
        : url;

const needsBar = (item) =>
    getFieldVal({ item, fieldName: "date" }) &&
    getFieldVal({ item, fieldName: "document_id" });

const resultLinkClasses = (doc) => ({
    external:
        DOCUMENT_TYPES_MAP[getFieldVal({ item: doc, fieldName: "type" })] ===
            "Public" ||
        getFieldVal({ item: doc, fieldName: "type" }) === "internal_link",
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
        <h2
            v-if="view !== 'search' && searchQuery"
            class="search-results__heading"
        >
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
            <template v-if="view !== 'search'">
                <span v-if="searchQuery">
                    for
                    <span class="search-query__span">{{
                        searchQuery
                    }}</span></span
                >
                <span v-if="searchQuery && selectedSubjectParts[0]">
                    within {{ selectedSubjectParts[1][0] }}</span
                >
            </template>
        </div>
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
                    :href="
                        apiUrl +
                        'resources/' +
                        getFieldVal({ item: doc, fieldName: 'id' }) +
                        '/edit'
                    "
                >
                    Edit
                    <i class="fas fa-edit"></i>
                </a>
            </template>
            <template #labels>
                <DocTypeLabel
                    v-if="
                        !_isEmpty(getFieldVal({ item: doc, fieldName: 'type' }))
                    "
                    :icon-type="getFieldVal({ item: doc, fieldName: 'type' })"
                    :doc-type="
                        DOCUMENT_TYPES_MAP[
                            getFieldVal({ item: doc, fieldName: 'type' })
                        ]
                    "
                />
                <template
                    v-if="
                        DOCUMENT_TYPES_MAP[
                            getFieldVal({ item: doc, fieldName: 'type' })
                        ] === 'Internal'
                    "
                >
                    <CategoryLabel
                        v-if="
                            !_isEmpty(
                                getFieldVal({
                                    item: doc,
                                    fieldName: 'category',
                                })
                            )
                        "
                        :name="
                            getFieldVal({ item: doc, fieldName: 'category' }) &&
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .parent
                                ? getParentCategoryName({
                                      item: doc,
                                      categoriesArr: categories,
                                  })
                                : getFieldVal({
                                      item: doc,
                                      fieldName: 'category',
                                  }).name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="
                            getFieldVal({ item: doc, fieldName: 'category' }) &&
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .parent
                        "
                        :name="
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .name
                        "
                        type="subcategory"
                    />
                </template>
                <template v-else>
                    <CategoryLabel
                        v-if="
                            !_isEmpty(
                                getFieldVal({
                                    item: doc,
                                    fieldName: 'category',
                                })
                            )
                        "
                        :name="
                            getFieldVal({ item: doc, fieldName: 'category' }) &&
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .parent
                                ? getParentCategoryName({
                                      item: doc,
                                      categoriesArr: categories,
                                  })
                                : getFieldVal({
                                      item: doc,
                                      fieldName: 'category',
                                  }).name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="
                            getFieldVal({ item: doc, fieldName: 'category' }) &&
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .parent
                        "
                        :name="
                            getFieldVal({ item: doc, fieldName: 'category' })
                                .name
                        "
                        type="subcategory"
                    />
                </template>
            </template>
            <template #context>
                <span
                    v-if="getFieldVal({ item: doc, fieldName: 'date' })"
                    class="result__context--date"
                    :class="needsBar(doc) && 'result__context--date--bar'"
                    >{{
                        formatDate(
                            getFieldVal({ item: doc, fieldName: "date" })
                        )
                    }}</span
                >
                <!-- DivisionLabel
                    v-if="doc.type === 'internal' && doc.division"
                    :division="doc.division"
                /-->
                <span
                    v-if="getFieldVal({ item: doc, fieldName: 'document_id' })"
                    >{{
                        getFieldVal({ item: doc, fieldName: "document_id" })
                    }}</span
                >
            </template>
            <template #link>
                <a
                    :href="getUrl(doc.resource ? doc.resource : doc)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="document__link document__link--filename"
                    :class="resultLinkClasses(doc)"
                    v-html="
                        getResultLinkText(doc) +
                        getFileTypeButton({
                            fileName: getFieldVal({
                                item: doc,
                                fieldName: 'file_name',
                            }),
                            uid: getFieldVal({ item: doc, fieldName: 'uid' }),
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
                    v-if="
                        getFieldVal({ item: doc, fieldName: 'subjects' }) &&
                        getFieldVal({ item: doc, fieldName: 'subjects' })
                            .length > 0
                    "
                    class="document__info-block"
                >
                    <SubjectChips
                        :subjects="
                            getFieldVal({ item: doc, fieldName: 'subjects' })
                        "
                    />
                </div>
            </template>
            <template #sections>
                <RelatedSections
                    :base="base"
                    :item="doc.resource ? doc.resource : doc"
                    :parts-last-updated="partsLastUpdated"
                    label="Related Regulation Citation"
                />
            </template>
        </ResultsItem>
    </div>
</template>
