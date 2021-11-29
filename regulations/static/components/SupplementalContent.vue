<template>
    <div class="supplemental-content-container">
        <template v-if="isFetching">
            <simple-spinner></simple-spinner>
        </template>
        <template v-else>
            <supplemental-content-category
                v-for="(category, index) in categories"
                :key="index"
                :name="category.name"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
            >
            </supplemental-content-category>
        </template>
    </div>
</template>

<script>
import SimpleSpinner from "./SimpleSpinner.vue";
import SupplementalContentCategory from "./SupplementalContentCategory.vue";

export default {
    components: {
        SupplementalContentCategory,
        SimpleSpinner,
    },

    props: {
        api_url: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        sections: {
            type: Array,
            required: true,
        },
    },

    data() {
        return {
            isFetching: true,
            categories: [],
        };
    },

    created() {
        this.fetch_content(this.title, this.part, this.sections);
    },

    methods: {
        async fetch_content(title, part, sections) {
            const joinedSections = sections.join("&sections=");
            const response = await fetch(
                `${this.api_url}title/${title}/part/${part}/supplemental_content?&sections=${joinedSections}`
            );
            const content = await response.json();
            this.categories = content;
            this.isFetching = false;
        },
    },
};
</script>
