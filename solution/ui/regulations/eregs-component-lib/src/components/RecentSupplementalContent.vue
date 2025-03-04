<script setup>
import { computed } from "vue";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import SupplementalContentObject from "./SupplementalContentObject.vue";
import SubjectChips from "spaComponents/subjects/SubjectChips.vue";

const props = defineProps({
    supplementalContent: {
        type: Array,
        required: true,
    },
    limit: {
        type: Number,
        required: false,
        default: 3,
    },
});

const limitedContent = computed(() => {
    return props.supplementalContent.slice(0, props.limit);
});
</script>

<template>
    <div class="supplemental-content-list">
        <template
            v-for="(content, index) in limitedContent"
            :key="content.category.name + index"
        >
            <div class="category-labels">
                <CategoryLabel :name="content.category.name" type="category" />
            </div>
            <SupplementalContentObject
                :name="content.document_id"
                :description="content.title"
                :date="content.date"
                :url="content.url"
            />
            <SubjectChips :subjects="content.subjects" />
            <div class="spacer" />
        </template>
    </div>
</template>
