<script setup>
import { computed, inject } from "vue";

import {
    hasRegulationCitations,
    hasStatuteCitations,
} from "utilities/utils";

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import RelatedSectionsCollapse from "sharedComponents/results-item-parts/RelatedSectionsCollapse.vue";
import SupplementalContentObject from "./SupplementalContentObject.vue";
import SubjectChips from "spaComponents/subjects/SubjectChips.vue";

const props = defineProps({
    limit: {
        type: Number,
        required: false,
        default: 3,
    },
    partsLastUpdated: {
        type: Object,
        required: true,
    },
    supplementalContent: {
        type: Array,
        required: true,
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
                :uid="content.uid ?? content.id"
            />
            <SubjectChips :subjects="content.subjects" />
            <RelatedSectionsCollapse
                v-if="
                    content.type !== 'reg_text' &&
                        (hasRegulationCitations({ doc: content, partsLastUpdated })
                            || hasStatuteCitations({ doc: content }))"
                :item="content"
                :base-url="content.url"
                :parts-last-updated="partsLastUpdated"
                :has-statute-citations="hasStatuteCitations({ doc: content })"
                :has-regulation-citations="hasRegulationCitations({ doc: content, partsLastUpdated })"
            />
            <div class="spacer" />
        </template>
    </div>
</template>
