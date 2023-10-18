<script setup>
import { inject } from "vue";

import { formatDate } from "utilities/filters";

import RelatedSections from "sharedComponents/results-item-parts/RelatedSections.vue";
import SubjectChips from "sharedComponents/results-item-parts/SubjectChips.vue";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";

const props = defineProps({
    results: {
        type: Array,
        default: () => [],
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
});

const apiUrl = inject("apiUrl");
const base = inject("base");

const getDownloadUrl = (uid) => `${apiUrl}file-manager/files/${uid}`;
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
            <template #labels>
                <CategoryLabel
                    v-if="doc.document_type"
                    :name="doc.document_type.name"
                    type="category"
                />
            </template>
            <template #context>
                <span
                    v-if="doc.date"
                    class="result__context--date"
                    >{{ formatDate(doc.date) }}</span
                >
            </template>
            <template #link>
                <h3>
                    <a
                        :href="getDownloadUrl(doc.uid)"
                        class="document__link document__link--filename"
                        >{{ doc.document_id }}</a
                    >
                </h3>
            </template>
            <template #snippet>
                <div v-if="doc.summary">{{ doc.summary }}</div>
            </template>
            <template #chips>
                <div v-if="doc.subject.length > 0" class="document__info-block">
                    <SubjectChips :subjects="doc.subject" />
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
