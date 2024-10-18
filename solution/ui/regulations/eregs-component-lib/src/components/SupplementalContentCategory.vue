<template>
    <div
        v-if="hasChildren || (!hasChildren && showIfEmpty)"
        class="supplemental-content-category"
    >
        <div class="category">
            <collapse-button
                v-if="hasChildren"
                :class="collapseButtonClasses"
                :name="name"
                state="collapsed"
                class="category-title"
            >
                <template #expanded
                    >{{ name }}
                    <i v-if="hasChildren" class="fa fa-chevron-up"></i
                ></template>
                <template #collapsed
                    >{{ name }}
                    <i v-if="hasChildren" class="fa fa-chevron-down"></i
                ></template>
            </collapse-button>
            <div v-else class="category-title childless collapsible-title">
                {{ name }}
            </div>
            <span v-if="isFetching"></span>
            <span
                v-else-if="!hasChildren"
                class="childless category-description"
                >None</span
            >
            <span v-else-if="showDescription" class="category-description">{{
                description
            }}</span>

            <collapsible
                :name="name"
                state="collapsed"
                class="collapse-content"
                overflow
            >
                <supplemental-content-category
                    v-for="category in subcategories"
                    :key="category.name"
                    :subcategory="true"
                    :name="category.name"
                    :description="category.description"
                    :supplemental_content="category.supplemental_content"
                    :sub_categories="category.subcategories"
                    :is-fetching="isFetching"
                >
                </supplemental-content-category>
                <template v-if="isFrLinkCategory">
                    <related-rule-list
                        v-if="supplemental_content"
                        :rules="supplemental_content"
                    />
                </template>
                <template v-else>
                    <supplemental-content-list
                        v-if="supplemental_content"
                        :supplemental_content="supplemental_content"
                        :has-subcategories="hasSubcategories"
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
        subcategories: {
            type: Array,
            required: false,
        },
        isFrLinkCategory: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    computed: {
        showDescription() {
            return this.description && !/^\s*$/.test(this.description);
        },
        hasSubcategories() {
            return this?.subcategories?.length ?? 0;
        },
        hasChildren() {
            return !!(
                this.supplemental_content?.length ||
                (this.subcategories &&
                    this.subcategories.some(
                        (subcategory) => subcategory.supplemental_content
                    ))
            );
        },
        collapseButtonClasses() {
            return {
                subcategory: this.subcategory,
                "is-fr-link-btn": this.isFrLinkCategory,
            };
        },
    },
};
</script>
