<template>
    <div class="supplementary-content-category">
        <div class="category-toggle-container">
            <collapse-button :name="title" state="collapsed" class="category-toggle">
                <template v-slot:expanded><i class="fa fa-chevron-up"></i></template>
                <template v-slot:collapsed><i class="fa fa-chevron-down"></i></template>
            </collapse-button>
        </div>
        <div class="category">
            <h3 class="category-title" v-bind:class="{ subcategory: subcategory }">{{ title }}</h3>
            <span class="category-description">{{ description }}</span>
            <collapsible :name="title" state="collapsed" direction="vertical" class="category-content">
                <supplementary-content-category v-for="(category, index) in sub_categories" :key="index"
                    :subcategory="true"
                    :title="category.title"
                    :description="category.description"
                    :supplementary_content="category.supplementary_content"
                    :sub_categories="category.sub_categories">
                </supplementary-content-category>
                <supplementary-content-list :supplementary_content="supplementary_content" />
            </collapsible>
        </div>
    </div>
</template>

<script>
import SupplementaryContentList from './SupplementaryContentList.vue'
import CollapseButton from './CollapseButton.vue'
import Collapsible from './Collapsible.vue'

export default {
    name: 'supplementary-content-category',

    components: {
        SupplementaryContentList,
        CollapseButton,
        Collapsible,
    },

    props: {
        subcategory: {
            type: Boolean,
            required: false,
            default: false,
        },
        title: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        supplementary_content: {
            type: Array,
            required: false,
        },
        sub_categories: {
            type: Array,
            required: false,
        },
    },
};
</script>
