<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
    results: {
        type: Array,
        default: () => [],
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
            <p>Related Citations:</p>
            <p
                v-for="loc in doc.locations"
                :key="loc.title + loc.part + loc.section_id"
            >
                {{ loc.title }} CFR § {{ loc.part }}.{{ loc.section_id }}
            </p>
        </div>
    </div>
</template>

<style></style>
