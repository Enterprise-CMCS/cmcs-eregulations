<script setup>
import _groupBy from "lodash/groupBy";

import { computed, ref } from "vue";

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
});

const locationsCount = props.item.locations.length;
const groupedLocations = _groupBy(props.item.locations, "title");
</script>

<template>
    <div class="related-sections">
        <span class="related-sections-title">
            Related Section<span v-if="locationsCount !== 1">s</span>:
        </span>
        <template v-if="locationsCount > 0">
            <template v-for="(locations, title, i) in groupedLocations">
                <span :key="title + i" class="title__span"
                    >{{ title }} CFR
                </span>
                <span
                    :key="i + title"
                    v-if="locations.length > 1"
                    class="section-sign"
                    >§§
                </span>
                <span :key="i + title" v-else class="section-sign">§ </span>
                <template v-for="(location, i) in locations">
                    <span
                        :key="location.display_name + i"
                        class="related-section-link"
                    >
                        <a :href="locationUrl(location, base)">{{
                            locationLabel(location)
                        }}</a>
                        <span v-if="i + 1 != locations.length">, </span>
                    </span>
                </template>
                <span
                    :key="i + title + i"
                    v-if="i + 1 != Object.keys(groupedLocations).length"
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
