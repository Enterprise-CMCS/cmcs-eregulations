<template>
    <div class="supplemental-content-category">
        <div class="category">
            <collapse-button v-bind:class="{ subcategory: subcategory }" :name="name" state="collapsed" class="category-title">
                <template v-slot:expanded>{{ name }} <i class="fa fa-chevron-up"></i></template>
                <template v-slot:collapsed>{{ name }} <i class="fa fa-chevron-down"></i></template>
            </collapse-button>
            <span v-if="showDescription" class="category-description">{{
                description
            }}</span>
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
                >
                </supplemental-content-category>
                <supplemental-content-list
                    :supplemental_content="supplemental_content"
                    :has_sub_categories="has_sub_categories"
                />
            </collapsible>
        </div>
    </div>
</template>

<script>
import SupplementalContentList from "./SupplementalContentList.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

export default {
    name: "supplemental-content-category",

    components: {
        SupplementalContentList,
        CollapseButton,
        Collapsible,
    },

    props: {
        subcategory: {
            type: Boolean,
            required: false,
            default: false,
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
        showDescription: function () {
            return this.description && !/^\s*$/.test(this.description);
        },
        has_sub_categories() {
            return this.sub_categories.length;
        },
    },
};
</script>
