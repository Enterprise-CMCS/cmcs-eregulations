<template>
    <div
        v-if="has_children || (!has_children && showIfEmpty)"
        class="supplemental-content-category"
    >
        <div class="category">
            <collapse-button
                v-if="has_children"
                :class="collapseButtonClasses"
                :name="name"
                state="collapsed"
                class="category-title"
            >
                <template #expanded
                    >{{ name }}
                    <i v-if="has_children" class="fa fa-chevron-up"></i
                ></template>
                <template #collapsed
                    >{{ name }}
                    <i v-if="has_children" class="fa fa-chevron-down"></i
                ></template>
            </collapse-button>
            <div v-else class="category-title childless collapsible-title">
                {{ name }}
            </div>
            <span v-if="isFetching"></span>
            <span
                v-else-if="!has_children"
                class="childless category-description"
                >None</span
            >
            <span v-else-if="showDescription" class="category-description">{{
                description
            }}</span>

            <collapsible
                :name="name"
                state="collapsed"
                class="category-content"
                overflow
            >
                <supplemental-content-category
                    v-for="category in sub_categories"
                    :key="category.name"
                    :subcategory="true"
                    :name="category.name"
                    :description="category.description"
                    :supplemental_content="category.supplemental_content"
                    :sub_categories="category.sub_categories"
                    :isFetching="isFetching"
                >
                </supplemental-content-category>
                <template
                    v-if="isFrDocCategory"
                >
                    <related-rule-list
                        v-if="supplemental_content"
                        :rules="supplemental_content"
                    />
                </template>
                <template v-else>
                    <supplemental-content-list
                        v-if="supplemental_content"
                        :supplemental_content="supplemental_content"
                        :has_sub_categories="has_sub_categories"
                    />
                </template>
            </collapsible>
        </div>
    </div>
</template>

<script>
import RelatedRuleList from "./RelatedRuleList.vue";
import SupplementalContentList from "./SupplementalContentList.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

export default {
    name: "supplemental-content-category",

    components: {
        RelatedRuleList,
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
        isFetching: {
            type: Boolean,
            required: false,
            default: true,
        },
        name: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        showIfEmpty: {
            type: Boolean,
            required: false,
            default: false,
        },
        supplemental_content: {
            type: Array,
            required: false,
        },
        sub_categories: {
            type: Array,
            required: false,
        },
        isFrDocCategory: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    computed: {
        showDescription() {
            return this.description && !/^\s*$/.test(this.description);
        },
        has_sub_categories() {
            return this?.sub_categories?.length ?? 0;
        },
        has_children() {
            return (
                this.sub_categories?.length || this.supplemental_content?.length
            );
        },
        collapseButtonClasses() {
            return {
                subcategory: this.subcategory,
                "is-fr-doc-btn": this.isFrDocCategory,
            };
        },
    },
};
</script>
