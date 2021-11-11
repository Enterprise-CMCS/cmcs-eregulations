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
        <collapsible :name="innerName" state="collapsed" class="category-content">
            <supplemental-content-object
                v-for="(content, index) in additionalContent"
                :key="index"
                :name="content.name"
                :description="content.description"
                :date="content.date"
                :url="content.url"
            >
            </supplemental-content-object>
        </collapsible>
        <collapse-button
            v-if="showMoreNeeded"
            v-bind:class="{ subcategory: subcategory }"
            :name="innerName"
            state="collapsed"
            class="category-title"
        >
            <template v-slot:expanded>
                <show-more-button :count="contentCount"></show-more-button>
            </template>
            <template v-slot:collapsed>
                <show-more-button :count="contentCount"></show-more-button>
            </template>
        </collapse-button>
    </div>
</template>

<script>
import SupplementalContentObject from "./SupplementalContentObject.vue";
import ShowMoreButton from "./ShowMoreButton.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

export default {
    name: "supplemental-content-list",

    components: {
        SupplementalContentObject,
        ShowMoreButton,
        CollapseButton,
        Collapsible,
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
            innerName: Math.random().toString(36).replace(/[^a-z]+/g, '')
        };
    },

    computed: {
        limitedContent() {
            return this.supplemental_content.slice(0, this.limit);
        },
        additionalContent() {
            return this.supplemental_content.slice(this.limit);
        },
        contentCount() {
            return this.supplemental_content.length;
        },
        showMoreNeeded() {
            return this.contentCount > this.limit;
        },
    },
};
</script>
