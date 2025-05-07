<script setup>
import { computed } from "vue";
import RelatedRuleList from "./RelatedRuleList.vue";
import SupplementalContentList from "./SupplementalContentList.vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";

const props = defineProps({
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
    supplemental_content: { // eslint-disable-line vue/prop-name-casing
        type: Array,
        required: false,
        default: undefined,
    },
    subcategories: {
        type: Array,
        required: false,
        default: undefined,
    },
    isFrLinkCategory: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const showDescription = computed(() => {
    return props.description && !/^\s*$/.test(props.description);
});

const hasSubcategories = computed(() => {
    return props?.subcategories?.length ?? 0;
});

const hasChildren = computed(() => {
    return !!(
        props.supplemental_content?.length ||
        (props.subcategories &&
            props.subcategories.some(
                (subcategory) => subcategory.supplemental_content
            ))
    );
});

const collapseButtonClasses = computed(() => {
    return {
        subcategory: props.subcategory,
        "is-fr-link-btn": props.isFrLinkCategory,
    };
});
</script>

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
                <template #expanded>
                    {{ name }}
                    <i v-if="hasChildren" class="fa fa-chevron-up" />
                </template>
                <template #collapsed>
                    {{ name }}
                    <i v-if="hasChildren" class="fa fa-chevron-down" />
                </template>
            </collapse-button>
            <div v-else class="category-title childless collapsible-title">
                {{ name }}
            </div>
            <span v-if="isFetching" />
            <span
                v-else-if="!hasChildren"
                class="childless category-description"
            >None</span>
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
                />
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
