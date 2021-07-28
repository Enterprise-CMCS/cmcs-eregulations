<template>
    <div class="supplementary-content-category">
        <h3>{{ title }}</h3>
        <collapse-button :name="title" state="collapsed">
            <template v-slot:expanded><i class="fa fa-chevron-up"></i></template>
            <template v-slot:collapsed><i class="fa fa-chevron-down"></i></template>
        </collapse-button>
        <collapsible :name="title" state="collapsed" direction="vertical"> 
            <supplementary-content-category v-for="(category, index) in sub_categories" :key="index"
                :title="category.title"
                :description="category.description"
                :supplementary_content="category.supplementary_content"
                :sub_categories="category.sub_categories">
            </supplementary-content-category>
            <supplementary-content-list :supplementary_content="supplementary_content" />
        </collapsible>
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
