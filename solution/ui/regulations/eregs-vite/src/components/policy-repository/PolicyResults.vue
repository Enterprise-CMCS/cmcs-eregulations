<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router/composables";

import _isEmpty from "lodash/isEmpty";

import { formatDate } from "utilities/filters";
import { getFileNameSuffix } from "utilities/utils";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import RelatedSections from "sharedComponents/results-item-parts/RelatedSections.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";

import SubjectChips from "./SubjectChips.vue";

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

const resultLinkClasses = () => ({
    "document__link--search": !!$route?.query?.q,
});

const resultLinkLabel = (item) => {
    const fileTypeSuffix = getFileNameSuffix(item.file_name_string);
    const fileTypeButton =
        item.file_name_string && fileTypeSuffix
            ? `<span data-testid="download-chip-${
                  item.url
              }" class="result__link--file-type">Download ${fileTypeSuffix.toUpperCase()}</span>`
            : null;

    const linkText =
        item.resource_type === "external"
            ? item.summary_headline || item.summary_string
            : item.document_name_headline || item.doc_name_string;

    return `<span class='result__link--label'>${linkText}</span>${
        fileTypeButton ?? ""
    }`;
};

const editUrl = (doc) => {
    const stage_env = process.env.STAGE_ENV	 || '';
    const baseUrl = stage_env === 'prod' ? '' : stage_env;
    return `${baseUrl}/v3/content-search/resource/${doc.id}`;
};
</script>

<template>
    <div class="doc__list">
        <div class="search-results-count">
            <span v-if="results.length > 0">
                Showing 1 -
                {{ results.length }} of
            </span>
            {{ results.length }} document<span v-if="results.length != 1"
                >s</span
            >.
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
                    :href="editUrl(doc)"
                >
                    Edit
                    <i class="fas fa-edit"></i>
                </a>
            </template>
            <template #labels>
                <CategoryLabel
                    v-if="!_isEmpty(doc.document_type)"
                    :name="doc.document_type.name"
                    type="category"
                />
                <CategoryLabel
                    v-else-if="!_isEmpty(doc.category)"
                    :name="
                        doc.category.parent
                            ? doc.category.parent.name
                            : doc.category.name
                    "
                    type="category"
                />
                <CategoryLabel
                    v-if="doc.category?.parent"
                    :name="doc.category.name"
                    type="subcategory"
                />
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
                <h3>
                    <a
                        :href="getUrl(doc)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="document__link document__link--filename"
                        :class="resultLinkClasses(doc)"
                        v-html="resultLinkLabel(doc)"
                    ></a>
                </h3>
            </template>
            <template #snippet>
                <div
                    v-if="
                        doc.resource_type === 'internal' &&
                        (doc.summary_headline || doc.summary_string)
                    "
                    v-html="doc.summary_headline || doc.summary_string"
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
