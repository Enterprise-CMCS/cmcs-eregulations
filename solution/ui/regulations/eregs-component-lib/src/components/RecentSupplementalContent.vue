<script>
import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import SupplementalContentObject from "./SupplementalContentObject.vue";
import SubjectChips from "spaComponents/subjects/SubjectChips.vue";

export default {
    name: "RecentSupplementalContent",

    components: {
        CategoryLabel,
        SubjectChips,
        SupplementalContentObject,
    },

    props: {
        supplementalContent: {
            type: Array,
            required: true,
        },
        limit: {
            type: Number,
            required: false,
            default: 3,
        },
    },

    computed: {
        limitedContent() {
            return this.supplementalContent.slice(0, this.limit);
        },
    },
};
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
