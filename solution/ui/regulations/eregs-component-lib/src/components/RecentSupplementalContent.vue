<script>
import SupplementalContentObject from "./SupplementalContentObject.vue";

export default {
    name: "RecentSupplementalContent",

    components: {
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
        <template v-for="(content, index) in limitedContent">
            <div :key="content.category.name + index" class="category-labels">
                <div class="result-label category-label">
                    {{ content.category.name }}
                </div>
            </div>
            <supplemental-content-object
                :key="index"
                :name="content.name"
                :description="content.description"
                :date="content.date"
                :url="content.url"
            >
            </supplemental-content-object>
        </template>
    </div>
</template>
