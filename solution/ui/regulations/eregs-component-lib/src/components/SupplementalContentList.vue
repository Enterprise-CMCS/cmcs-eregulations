<template>
    <div class="supplemental-content-list">
        <supplemental-content-object
            v-for="(content, index) in limitedContent"
            :key="index"
            :name="content.document_id"
            :description="content.title || content.doc_name_string"
            :date="content.date || content.date_string"
            :division="content.division"
            :uid="content.uid"
            :url="content.url"
            :doc-type="content.type ?? 'external'"
            :file-name="content.file_name"
        />
        <collapse-button
            v-if="showMoreNeeded"
            :class="{ subcategory: subcategory }"
            :name="innerName"
            state="collapsed"
            class="category-title show-more"
        >
            <template #expanded>
                <show-more-button
                    button-text="- Show Less"
                    :count="contentCount"
                />
            </template>
            <template #collapsed>
                <show-more-button
                    button-text="+ Show More"
                    :count="contentCount"
                />
            </template>
        </collapse-button>
        <collapsible
            :name="innerName"
            state="collapsed"
            class="collapse-content show-more-content"
        >
            <supplemental-content-object
                v-for="(content, index) in additionalContent"
                :key="index"
                :name="content.document_id"
                :description="content.title || content.doc_name_string"
                :date="content.date || content.date_string"
                :uid="content.uid"
                :url="content.url"
                :doc-type="content.type ?? 'external'"
            />
            <collapse-button
                v-if="showMoreNeeded && contentCount > 10"
                :class="{ subcategory: subcategory }"
                :name="innerName"
                state="collapsed"
                class="category-title show-more"
            >
                <template #expanded>
                    <show-more-button
                        button-text="- Show Less"
                        :count="contentCount"
                    />
                </template>
                <template #collapsed>
                    <show-more-button
                        button-text="+ Show More"
                        :count="contentCount"
                    />
                </template>
            </collapse-button>
        </collapsible>
    </div>
</template>

<script>
/* eslint-disable vue/prop-name-casing */
import SupplementalContentObject from "./SupplementalContentObject.vue";
import ShowMoreButton from "./ShowMoreButton.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

export default {
    name: "SupplementalContentList",

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
        hasSubcategories: {
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
