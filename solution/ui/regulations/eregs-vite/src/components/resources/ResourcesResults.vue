<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
        <template v-for="(item, idx) in results">
            <div :key="item.created_at + idx">
                <div class="category-labels">
                    <div class="result-label category-label">
                        {{
                            item.category.parent
                                ? item.category.parent.name
                                : item.category.name
                        }}
                    </div>
                    <div
                        v-if="item.category.parent"
                        class="result-label subcategory-label"
                    >
                        {{ item.category.name }}
                    </div>
                </div>
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
                <RelatedSections
                    :base="base"
                    :item="item"
                    :parts-last-updated="partsLastUpdated"
                    :parts-list="partsList"
                />
            </div>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>

<script>
import { locationLabel, locationUrl } from "../../utilities/filters";

import RelatedSections from "@/components/search/RelatedSections.vue";
import SupplementalContentObject from "eregsComponentLib/src/components/SupplementalContentObject.vue";

export default {
    name: "ResourcesResults",

    components: {
        SupplementalContentObject,
    },

    props: {
        base: {
            type: String,
            required: true,
        },
        partsLastUpdated: {
            type: Object,
            required: true,
        },
        partsList: {
            type: Array,
            required: true,
        },
        results: {
            type: Array,
            default: () => [],
        },
    },

    methods: { locationLabel, locationUrl },
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

.related-sections {
    margin-bottom: 40px;
    font-size: $font-size-xs;
    color: $mid_gray;

    .related-sections-title {
        font-weight: 600;
        color: $dark_gray;
    }

    a {
        text-decoration: none;
    }
}
</style>
