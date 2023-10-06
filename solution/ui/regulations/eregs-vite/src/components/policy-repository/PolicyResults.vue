<script setup>
import { inject } from "vue";

import RelatedSections from "@/components/search/RelatedSections.vue";

import SubjectChips from "eregsComponentLib/src/components/shared-components/PolicyRepository/SubjectChips.vue";

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
        <div v-for="doc in results" :key="doc.uid" class="doc-list__document">
            <div class="document__primary-info document__info-block">
                <div v-if="doc.document_type" class="document__type">
                    <h3>{{ doc.document_type.name }}</h3>
                </div>
                <div class="document__filename">
                    <h3>
                        <a
                            :href="getDownloadUrl(doc.uid)"
                            class="document__link document__link--filename"
                            >{{ doc.document_name }}</a
                        >
                    </h3>
                </div>
            </div>
            <template v-if="doc.subject.length > 0">
                <div class="document__info-block">
                    <SubjectChips
                        :subjects="doc.subject"
                    />
                </div>
            </template>
            <div class="document__info-block">
                <a
                    :href="getDownloadUrl(doc.uid)"
                    class="document__link document__link--view"
                    >View Document</a
                >
            </div>
            <div class="document__info-block">
                <RelatedSections
                    :item="doc"
                    :parts-last-updated="partsLastUpdated"
                    label="Related Regulation Citation"
                />
            </div>
        </div>
    </div>
</template>

<style></style>
