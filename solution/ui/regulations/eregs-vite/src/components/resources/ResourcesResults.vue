<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
        <template v-for="(item, idx) in results">
            <ResultsItem :key="item.created_at + idx">
                <template #labels>
                    <Label
                        :name="
                            item.category.parent
                                ? item.category.parent.name
                                : item.category.name
                        "
                        type="category"
                    />
                    <Label
                        v-if="item.category.parent"
                        :name="item.category.name"
                        type="subcategory"
                    />
                </template>
                <template #context>
                    <div style="margin-bottom: -8px"></div>
                </template>
                <template #link>
                    <div style="margin-bottom: -8px"></div>
                </template>
                <template #resources-content>
                    <div class="result-content-wrapper">
                        <SupplementalContentObject
                            :name="item.name"
                            :description="
                                item.descriptionHeadline || item.description
                            "
                            :date="item.date"
                            :url="item.url"
                        />
                    </div>
                </template>
                <template #sections>
                    <RelatedSections
                        :base="base"
                        :item="item"
                        :parts-last-updated="partsLastUpdated"
                    />
                </template>
            </ResultsItem>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>

<script>
import RelatedSections from "sharedComponents/results-item-parts/RelatedSections.vue";

import Label from "sharedComponents/results-item-parts/Label.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";
import SupplementalContentObject from "eregsComponentLib/src/components/SupplementalContentObject.vue";

export default {
    name: "ResourcesResults",

    components: {
        Label,
        RelatedSections,
        ResultsItem,
        SupplementalContentObject,
    },

    props: {
        base: {
            type: String,
            required: true,
        },
        results: {
            type: Array,
            default: () => [],
        },
        partsLastUpdated: {
            type: Object,
            default: () => {},
        },
    },
};
</script>

<style lang="scss">
.category-labels {
    margin-bottom: 5px;

    .result-label {
        display: inline-block;
        font-size: 11px;
        width: fit-content;
        margin-right: 5px;
        background: #e3eef9;
        border-radius: 3px;
        padding: 2px 5px 3px;

        &.category-label {
            font-weight: 600;
        }
    }
}

.result-content-wrapper {
    margin-bottom: 20px;

    .supplemental-content a.supplemental-content-link {
        .supplemental-content-date,
        .supplemental-content-title,
        .supplemental-content-description {
            font-size: $font-size-lg;
        }
    }
}

.resources-content-container {
    .related-sections {
        margin-bottom: 40px;
        color: $mid_gray;
        font-size: $font-size-xs;

        .related-sections-title {
            font-weight: 600;
            color: $dark_gray;
            text-transform: none;
            font-size: $font-size-xs;
        }

        .title__span, .section-sign, .related-sections-none {
            font-size: $font-size-xs;
        }

        a {
            text-decoration: none;
            font-size: $font-size-xs;
        }
    }
}
</style>
