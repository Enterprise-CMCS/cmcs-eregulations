<template>
    <div class="supplementary-content-category">
        <div class="category">
            <collapse-button v-bind:class="{ subcategory: subcategory }" :name="title" state="collapsed" class="category-title">
                <template v-slot:expanded>{{ title }}<i class="fa fa-chevron-up"></i></template>
                <template v-slot:collapsed>{{ title }}<i class="fa fa-chevron-down"></i></template>
            </collapse-button>
            <span v-if="showDescription" class="category-description">{{ description }}</span>
            <collapsible :name="title" state="collapsed" class="category-content">
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

    computed: {
        showDescription: function() {
            return (this.description && !/^\s*$/.test(this.description));
        },
    },
};
</script>
