<script setup>
import { locationLabel, locationUrl } from "../../utilities/filters";

import SupplementalContentObject from "eregsComponentLib/src/components/SupplementalContentObject.vue";

defineProps({
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
});
</script>

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
                <div class="related-sections">
                    <span class="related-sections-title">
                        Related Section<span v-if="item.locations.length > 1"
                            >s</span
                        >:
                    </span>
                    <span v-if="item.locations.length > 1">§§ </span>
                    <span v-else>§ </span>
                    <template v-for="(location, i) in item.locations">
                        <span
                            :key="location.display_name + i"
                            class="related-section-link"
                        >
                            <a
                                :href="
                                    locationUrl(
                                        location,
                                        partsList,
                                        partsLastUpdated,
                                        base
                                    )
                                "
                            >
                                {{ locationLabel(location) }}
                            </a>
                            <span v-if="i + 1 != item.locations.length">
                                |
                            </span>
                        </span>
                    </template>
                </div>
            </div>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>
