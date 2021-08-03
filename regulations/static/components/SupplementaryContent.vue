<template>
    <div class="supplementary-content-container">
        <supplementary-content-category v-for="(category, index) in categories" :key="index"
            :title="category.title"
            :description="category.description"
            :supplementary_content="category.supplementary_content"
            :sub_categories="category.sub_categories">
        </supplementary-content-category>
    </div>
</template>

<script>
import SupplementaryContentCategory from './SupplementaryContentCategory.vue'

export default {
    components: {
        SupplementaryContentCategory,
    },

    props: {
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
            categories: [],
        }
    },

    async created() {
        this.categories = await this.fetch_content(this.title, this.part, this.sections);
    },

    methods: {
        async fetch_content(title, part, sections) {
            const joinedSections = sections.join("&sections=");
            const response = await fetch(`http://localhost:8000/v2/title/${title}/part/${part}/supplementary_content?&sections=${joinedSections}`);
            const content = await response.json();
            return content;
        },
    }
};
</script>
