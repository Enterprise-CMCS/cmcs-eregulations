<template>
    <div class="resources-results">
        <slot name="empty-state"></slot>
        <template v-for="(item, idx) in results">
            <div :key="item.created_at + idx">
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
            </div>
        </template>
        <slot name="pagination"></slot>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";

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

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    filters: {
        locationLabel(value) {
            return value.type.toLowerCase() === "section"
                ? `${value.part}.${value.section_id}`
                : `${value.part} Subpart ${value.subpart_id}`;
        },
        locationUrl(value, partsList, partsLastUpdated, base) {
            // getting parent and partDate for proper link to section
            // e.g. /42/433/Subpart-A/2021-03-01/#433-10
            // is not straightforward with v2.  See below.
            // Thankfully v3 will add "latest" for date
            // and will better provide parent subpart in resource locations array.
            const { part, section_id, type, title, subpart_id } = value;
            const partDate = `${partsLastUpdated[part]}/`;

            // early return if related regulation is a subpart and not a section
            if (type.toLowerCase() === "subpart") {
                return `${base}/${title}/${part}/Subpart-${subpart_id}/${partDate}`;
            }
            const partObj = partsList.find((parts) => parts.name == part);
            const subpart = partObj?.sections?.[section_id];

            // todo: Figure out which no subpart sections are invalid and which are orphans
            return subpart
                ? `${base}/${title}/${part}/Subpart-${subpart}/${partDate}#${part}-${section_id}`
                : `${base}/${title}/${part}/${partDate}#${part}-${section_id}`;
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
