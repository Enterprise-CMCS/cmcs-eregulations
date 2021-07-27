<template>
    <div class="supplementary-content-list">
        <supplementary-content v-for="(content, index) in supplementary_content" :key="index"
            :title="content.title"
            :description="content.description"
            :date="content.date"
            :url="content.url">
        </supplementary-content>
    </div>
</template>

<script>
import SupplementaryContent from './SupplementaryContent.vue'
export default {
    name: 'supplementary-content-list',

    components: {
        SupplementaryContent,
    },

    props: {
        supplementary_content: Array,
    },

    computed: {

    },

    methods: {

    },

    filters: {

    },
};
</script>
