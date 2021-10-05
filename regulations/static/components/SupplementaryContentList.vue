<template>
    <div class="supplementary-content-list">
        <supplementary-content-object v-for="(content, index) in limitedContent" :key="index"
            :title="content.title"
            :description="content.description"
            :date="content.date"
            :url="content.url">
        </supplementary-content-object>
        <show-more-button v-if="showMoreNeeded" :showMore="showMore" :count="contentCount"></show-more-button>
    </div>
</template>

<script>
import SupplementaryContentObject from './SupplementaryContentObject.vue'
import ShowMoreButton from './ShowMoreButton.vue'

export default {
    name: 'supplementary-content-list',

    components: {
        SupplementaryContentObject,
        ShowMoreButton,
    },

    props: {
        supplemental_content: {
            type: Array,
            required: true,
        },
        limit: {
            type: Number,
            required: false,
            default: 5,
        },
    },

    data() {
        return {
            limitedList: true,
        }
    },

    computed: {
        limitedContent() {
            if(this.limitedList) {
                return this.supplemental_content.slice(0, this.limit);
            }
            return this.supplemental_content;
        },
        contentCount() {
            return this.supplemental_content.length;
        },
        showMoreNeeded() {
            return this.contentCount > this.limit;
        },
    },

    methods: {
        showMore() {
            this.limitedList = !this.limitedList;
        }
    },
};
</script>
