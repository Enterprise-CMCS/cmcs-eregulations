<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
{{ results }}
    </div>
</template>

<script>
import { locationLabel, locationUrl } from "utilities/filters";

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
