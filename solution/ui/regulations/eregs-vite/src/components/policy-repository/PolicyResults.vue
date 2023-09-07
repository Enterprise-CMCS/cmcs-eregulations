<script setup>
import { computed, ref } from "vue";

import RelatedSections from "@/components/search/RelatedSections.vue";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
    results: {
        type: Array,
        default: () => [],
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
});

const getDownloadUrl = (uid) => `${props.base}file_manager/file/${uid}`;

</script>

<template>
    <div class="doc__list">
        <div
            v-for="doc in results"
            :key="doc.uid"
            class="doc-list__item"
        >
            <div 
                v-if="doc.document_type"
                class="doc-list-item__doc-type"
            >
                <h3>{{ doc.document_type.name }}</h3>
            </div>
            <p>Name: {{ doc.name }}</p>
            <p>Description: {{ doc.description }}</p>
            <p>UID: {{ doc.uid }}</p>
            <a :href="getDownloadUrl(doc.uid)">Download</a>
            <RelatedSections
                :base="base"
                :item="doc"
                :parts-last-updated="partsLastUpdated"
                label="Related Regulation Citation"
            />
        </div>
    </div>
</template>

<style></style>
