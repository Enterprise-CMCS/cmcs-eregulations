<template>
    <div class="supplemental-content-container">
        <supplemental-content-category v-for="(category, index) in categories" :key="index"
            :name="category.name"
            :description="category.description"
            :supplemental_content="category.supplemental_content"
            :sub_categories="category.sub_categories">
        </supplemental-content-category>
    </div>
</template>

<script>
import SupplementalContentCategory from './SupplementalContentCategory.vue'

export default {
    components: {
        SupplementalContentCategory,
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
            required: false,
        },
        subparts: {
            type: Array,
            required: false,
        },
        subject_groups: {
            type: Array,
            required: false,
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
        join_locations() {
            const locations = ["sections", "subparts", "subjectgroups"];
            const arrays = [this.sections, this.subparts, this.subject_groups];
            let output = "";
            for (let i = 0; i < locations.length; i++) {
                if (arrays[i].length > 0) {
                    const queryString = "&" + locations[i] + "=";
                    output += queryString + arrays[i].join(queryString);
                }    
            }
            return output;
        },
        async fetch_content(title, part, sections) {
            const joinedLocations = this.join_locations();
            const response = await fetch(`${this.api_url}title/${title}/part/${part}/supplemental_content?${joinedLocations}`);
            const content = await response.json();
            return content;
        },
    }
};
</script>
