<template>
    <div class="supplemental-content-category">
        <div class="category">
            <collapse-button v-bind:class="{ subcategory: subcategory, childless: !has_children }" :name="name" state="collapsed" class="category-title">

              <template v-slot:expanded>{{ name }} <i v-if="has_children" class="fa fa-chevron-up"></i></template>
              <template v-slot:collapsed>{{ name }} <i v-if="has_children" class="fa fa-chevron-down"></i></template>
            </collapse-button>
            <span v-if="showDescription" class="category-description">{{ description }}</span>

            <collapsible
                :name="name"
                state="collapsed"
                class="category-content"
            >
                <supplemental-content-category
                    v-for="(category, index) in sub_categories"
                    :key="index"
                    :subcategory="true"
                    :name="category.name"
                    :description="category.description"
                    :supplemental_content="category.supplemental_content"
                    :sub_categories="category.sub_categories"
                    :isFetching="isFetching"
                >
                </supplemental-content-category>
                <supplemental-content-list
                    :supplemental_content="supplemental_content"
                    :has_sub_categories="has_sub_categories"
                    v-if="supplemental_content"
                />
            </collapsible>

        </div>
    </div>
</template>

<script>
import SupplementalContentList from "./SupplementalContentList.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";
import SimpleSpinner from "./SimpleSpinner.vue";

export default {
    name: "supplemental-content-category",

    components: {
        SupplementalContentList,
        CollapseButton,
        Collapsible,
        SimpleSpinner
    },

    props: {
        subcategory: {
            type: Boolean,
            required: false,
            default: false,
        },
        isFetching: {
            type: Boolean,
            required: false,
            default: true,
        },
        name: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        supplemental_content: {
            type: Array,
            required: false,
        },
        sub_categories: {
            type: Array,
            required: false,
        },
    },

    computed: {
        showDescription () {
            return this.description && !/^\s*$/.test(this.description) ;
        },
        has_sub_categories() {
            return this.sub_categories.length;
        },
        has_children () {
          return this.sub_categories?.length || this.supplemental_content?.length
        }
    },
};
</script>
