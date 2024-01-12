<template>
    <div class="supplemental-content-list" v-if="!has_sub_categories">
        <template v-for="(content, index) in limitedContent">
            <supplemental-content-object
                :key="index"
                :name="content.name"
                :description="content.description || content.doc_name_string"
                :date="content.date || content.date_string"
                :url="content.url"
                :doc-type="content.resource_type ?? 'external'"
            >
            </supplemental-content-object>
        </template>
        <collapse-button
            v-if="showMoreNeeded"
            :class="{ subcategory: subcategory }"
            :name="innerName"
            state="collapsed"
            class="category-title show-more"
        >
            <template v-slot:expanded>
                <show-more-button
                    buttonText="- Show Less"
                    :count="contentCount"
                ></show-more-button>
            </template>
            <template v-slot:collapsed>
                <show-more-button
                    buttonText="+ Show More"
                    :count="contentCount"
                ></show-more-button>
            </template>
        </collapse-button>
        <collapsible
            :name="innerName"
            state="collapsed"
            class="category-content show-more-content"
        >
            <supplemental-content-object
                v-for="(content, index) in additionalContent"
                :key="index"
                :name="content.name"
                :description="content.description || content.doc_name_string"
                :date="content.date || content.date_string"
                :url="content.url"
                :doc-type="content.resource_type ?? 'external'"
            >
            </supplemental-content-object>
            <collapse-button
                v-if="showMoreNeeded && contentCount > 10"
                :class="{ subcategory: subcategory }"
                :name="innerName"
                state="collapsed"
                class="category-title show-more"
            >
                <template v-slot:expanded>
                    <show-more-button
                        buttonText="- Show Less"
                        :count="contentCount"
                    ></show-more-button>
                </template>
                <template v-slot:collapsed>
                    <show-more-button
                        buttonText="+ Show More"
                        :count="contentCount"
                    ></show-more-button>
                </template>
            </collapse-button>
        </collapsible>
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
            type: Number,
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
            subcategory: "",
            innerName: "SupplementalContentCollapsible",
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
