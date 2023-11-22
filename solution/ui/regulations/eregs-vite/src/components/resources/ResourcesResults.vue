<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
        <template v-for="(item, idx) in results" :key="item.created_at + idx">
            <ResultsItem>
                <template #labels>
                    <CategoryLabel
                        :name="
                            item.category.parent
                                ? item.category.parent.name
                                : item.category.name
                        "
                        type="category"
                    />
                    <CategoryLabel
                        v-if="item.category.parent"
                        :name="item.category.name"
                        type="subcategory"
                    />
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

import CategoryLabel from "sharedComponents/results-item-parts/CategoryLabel.vue";
import ResultsItem from "sharedComponents/ResultsItem.vue";
import SupplementalContentObject from "eregsComponentLib/src/components/SupplementalContentObject.vue";

export default {
    name: "ResourcesResults",

    components: {
        CategoryLabel,
        RelatedSections,
        ResultsItem,
        SupplementalContentObject,
    },

    props: {
        results: {
            type: Array,
            default: () => [],
        },
        partsLastUpdated: {
            type: Object,
            default: () => {},
        },
    },

    inject: ["base"],
};
</script>

<style lang="scss">
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
</style>
