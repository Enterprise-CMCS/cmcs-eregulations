<script setup>
import _groupBy from "lodash/groupBy";

import { locationLabel, locationUrl } from "utilities/filters";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
    item: {
        type: Object,
        required: true,
    },
    label: {
        type: String,
        default: "Related Section",
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
});

const filteredLocations = props.item.cfr_citations
    ? props.item.cfr_citations.filter((location) => {
          const { part } = location;
          return props.partsLastUpdated[part];
      })
    : [];

const locationsCount = filteredLocations.length;
const groupedLocations = _groupBy(filteredLocations, "title");
</script>

<template>
    <div class="related-sections">
        <span class="related-sections-title">
            {{ label }}<span v-if="locationsCount !== 1">s</span>:
        </span>
        <template v-if="locationsCount > 0">
            <template
                v-for="(locations, title, i) in groupedLocations"
                :key="title + i"
            >
                <span class="title__span">{{ title }} CFR </span>
                <span
                    v-if="locations.length > 1"
                    :key="i + title"
                    class="section-sign"
                    >§§
                </span>
                <span v-else :key="i + title + i" class="section-sign">§ </span>
                <template
                    v-for="(location, j) in locations"
                    :key="location.display_name + j"
                >
                    <span class="related-section-link">
                        <a :href="locationUrl(location, base)">{{
                            locationLabel(location)
                        }}</a>
                        <span v-if="j + 1 != locations.length">, </span>
                    </span>
                </template>
                <span
                    v-if="i + 1 != Object.keys(groupedLocations).length"
                    :key="i + title + i"
                    class="pipe-separator"
                >
                    |
                </span>
            </template>
        </template>
        <template v-else>
            <span class="related-sections-none">None</span>
        </template>
    </div>
</template>

<style></style>
