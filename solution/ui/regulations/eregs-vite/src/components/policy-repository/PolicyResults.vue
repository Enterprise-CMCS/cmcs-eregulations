<script setup>
import { inject } from "vue";

import RelatedSections from "@/components/search/RelatedSections.vue";

import SubjectChip from "eregsComponentLib/src/components/shared-components/PolicyRepository/SubjectChip.vue";

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

const getDownloadUrl = (uid) => `${apiUrl}file_manager/file/${uid}`;
</script>

<template>
    <div class="doc__list">
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
                            >{{ doc.name }}</a
                        >
                    </h3>
                </div>
            </div>
            <template v-if="doc.subject.length > 0">
                <div class="document__info-block">
                    <div class="document__subjects">
                        <template
                            v-for="(subject, i) in doc.subject"
                            :key="subject.id + 'x' + i"
                        >
                            <SubjectChip :subject-name="subject.full_name" />
                        </template>
                    </div>
                </div>
            </template>
            <div class="document__info-block">
                <a :href="getDownloadUrl(doc.uid)" class="document__link document__link--view"
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
