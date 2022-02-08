<template>
    <div class="supplemental-content-container">
            <supplemental-content-category
                v-for="(category, index) in categories"
                :key="index"
                :name="category.name"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
            >

            </supplemental-content-category>

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

    created() {
       this.fetch_content(this.title, this.part);
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

    methods: {
        async fetch_content(title, part) {
            try {
                const response = await fetch(
                    `${this.api_url}title/${title}/part/${part}/supplemental_content?${this.joined_locations}`
                );
                await new Promise(r => setTimeout(r, 5000));
                const content = await response.json();
                const updatedContent = this.categories.map(category =>{
                  const newContent = content.find(c => c.name === category.name)
                  return newContent || category
                })

                this.categories = updatedContent;
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
    },
    mounted() {
      const rawCategories = JSON.parse(document.getElementById('categories').textContent)
      const rawSubCategories = JSON.parse(document.getElementById('sub_categories').textContent)
      this.categories = rawCategories.map(c => {
        const category = JSON.parse(JSON.stringify(c))
        category.sub_categories = rawSubCategories.filter(subcategory => subcategory.parent_id === category.id)
        return category
      })
  },
};
</script>
