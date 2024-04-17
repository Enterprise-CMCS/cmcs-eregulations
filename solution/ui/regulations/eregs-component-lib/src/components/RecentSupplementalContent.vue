<script>
import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import SupplementalContentObject from "./SupplementalContentObject.vue";

export default {
    name: "RecentSupplementalContent",

    components: {
        CategoryLabel,
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
                :name="content.name"
                :description="content.description"
                :date="content.date"
                :url="content.url"
            >
            </SupplementalContentObject>
        </template>
    </div>
</template>
