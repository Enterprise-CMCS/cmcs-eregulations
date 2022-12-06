<template>
    <div class="resources-results">
        <template v-if="filteredContent && filteredContent.length == 0">
            <SearchEmptyState
                :eregs_url="regulationsSearchUrl"
                eregs_url_label="eRegulations regulation text"
                eregs_sublabel="Medicaid & CHIP regulations"
                :query="query"
            />
        </template>
        <template v-else>
            <template v-for="(item, idx) in filteredContent">
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
                            Related Regulation<span
                                v-if="item.locations.length > 1"
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
                                        location
                                            | locationUrl(
                                                partsList,
                                                partsLastUpdated,
                                                base
                                            )
                                    "
                                >
                                    {{ location | locationLabel }}
                                </a>
                                <span v-if="i + 1 != item.locations.length">
                                    |
                                </span>
                            </span>
                        </template>
                    </div>
                </div>
            </template>
            <PaginationController
                :count="count"
                :page="page"
                :page-size="pageSize"
                view="resources"
            />
        </template>
    </div>
</template>

<script>
import PaginationController from "@/components/pagination/PaginationController.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";

export default {
    name: "ResourcesResults",

    components: {
        PaginationController,
        SearchEmptyState,
        SupplementalContentObject,
    },

    props: {
        base: {
            type: String,
            required: true,
        },
        count: {
            type: Number,
            required: false,
            default: 0,
        },
        filteredContent: {
            type: Array,
            default: () => [],
        },
        page: {
            type: Number,
            required: false,
            default: 1,
        },
        pageSize: {
            type: Number,
            required: false,
            default: 100,
        },
        partsLastUpdated: {
            type: Object,
            required: true,
        },
        partsList: {
            type: Array,
            required: true,
        },
        query: String,
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

    computed: {
        regulationsSearchUrl() {
            return `${this.base}/search/`;
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
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

<style></style>
