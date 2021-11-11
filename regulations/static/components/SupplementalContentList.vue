<template>
    <div class="supplemental-content-list" v-if="!has_sub_categories">
        <supplemental-content-object
            v-for="(content, index) in limitedContent"
            :key="index"
            :name="content.name"
            :description="content.description"
            :date="content.date"
            :url="content.url"
        >
        </supplemental-content-object>
        <show-more-button
            v-if="showMoreNeeded"
            :showMore="showMore"
            :count="contentCount"
        ></show-more-button>
    </div>
</template>

<script>
import SupplementalContentObject from "./SupplementalContentObject.vue";
import ShowMoreButton from "./ShowMoreButton.vue";

export default {
    name: "supplemental-content-list",

    components: {
        SupplementalContentObject,
        ShowMoreButton,
    },

    props: {
        supplemental_content: {
            type: Array,
            required: true,
        },
        has_sub_categories: {
            type: Boolean,
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
        };
    },

    computed: {
        limitedContent() {
            if (this.limitedList) {
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
        },
    },
};
</script>
