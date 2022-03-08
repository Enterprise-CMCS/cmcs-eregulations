<template>
    <div class="supplemental-content-container">
        <supplemental-content-category
            v-for="category in categories"
            :key="category.name"
            :name="category.name"
            :description="category.description"
            :supplemental_content="category.supplemental_content"
            :sub_categories="category.sub_categories"
            :isFetching="isFetching"
        >
        </supplemental-content-category>
        <simple-spinner v-if="isFetching"></simple-spinner>
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
            required: false,
            default: [],
        },
        subparts: {
            type: Array,
            required: false,
            default: [],
        },
    },

    data() {
        return {
            categories: [],
            isFetching: true,
        };
    },

    computed: {
        params_array: function () {
            return [
                ["sections", this.sections],
                ["subparts", this.subparts],
            ];
        },
        joined_locations: function () {
            let output = "";
            this.params_array.forEach(function (param) {
                if (param[1].length > 0) {
                    const queryString = "&" + param[0] + "=";
                    output += queryString + param[1].join(queryString);
                }
            });
            return output;
        },
    },

    watch: {
        sections() {
            this.categories = [];
            this.isFetching = true;
            this.fetch_content(this.title, this.part);
        },
        subparts() {
            this.categories = [];
            this.isFetching = true;
            this.fetch_content(this.title, this.part);
        },
    },

    created() {
        this.fetch_content(this.title, this.part);
    },

    mounted() {
        if (!document.getElementById("categories")) return;

        const rawCategories = JSON.parse(
            document.getElementById("categories").textContent
        );
        const rawSubCategories = JSON.parse(
            document.getElementById("sub_categories").textContent
        );

        this.categories = rawCategories.map((c) => {
            const category = JSON.parse(JSON.stringify(c));
            category.sub_categories = rawSubCategories.filter(
                (subcategory) => subcategory.parent_id === category.id
            );
            return category;
        });
    },

    methods: {
        async fetch_content(title, part) {
            try {
                const response = await fetch(
                    `${this.api_url}title/${title}/part/${part}/supplemental_content?${this.joined_locations}`
                );
                const content = await response.json();
                this.categories = content;
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
    },
};
</script>
