<script setup>
import { inject } from "vue";

import RelatedSections from "@/components/search/RelatedSections.vue";

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
        <div v-for="doc in results" :key="doc.uid" class="doc-list__item">
            <div v-if="doc.document_type" class="doc-list-item__doc-type">
                <h3>{{ doc.document_type.name }}</h3>
            </div>
            <div>
                <a
                    :href="getDownloadUrl(doc.uid)"
                    class="doc-list-item__file-name"
                    >File Name {{ name }}</a
                >
            </div>
            <template v-if="doc.subject.length > 0">
                <div class="doc-list-item__subjects">
                    <span
                        v-for="(subject, i) in doc.subject"
                        :key="subject.id + 'x' + i"
                    >
                        {{ subject.full_name }}
                        <span v-if="i + 1 != doc.subject.length">, </span>
                    </span>
                </div>
            </template>
            <div>
                <a :href="getDownloadUrl(doc.uid)">View Document</a>
            </div>
            <RelatedSections
                :item="doc"
                :parts-last-updated="partsLastUpdated"
                label="Related Regulation Citation"
            />
        </div>
    </div>
</template>

<style></style>
