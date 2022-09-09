<template>
    <div class="results-container">
        <div class="results-content">
            <hr class="top-rule" />
            <div class="results-count">
                <span v-if="isLoading">Loading...</span>
                <span v-else>
                    <span v-if="count > 0">{{ currentPageResultsRange[0] }} - {{ currentPageResultsRange[1] }} of</span>
                    {{ count }} result<span v-if="count != 1">s</span> in Resources
                </span>
                <div class="sort-control">
                    <span class="sort-control-label">Sort by</span>
                    <FancyDropdown
                        :button-title="sortMethodTitle"
                        :disabled="sortDisabled"
                    >
                        <v-list class="sort-options-list">
                            <v-list-item-group
                                v-model="sortOptions"
                                class="sort-options-list-item-group"
                            >
                                <template
                                    v-for="(sortOption, index) in sortOptions"
                                >
                                    <v-list-item
                                        :key="sortOption.value + index"
                                        :data-value="sortOption.value"
                                        :disabled="sortOption.disabled"
                                        :inactive="sortOption.disabled"
                                        @click="clickMethod"
                                    >
                                        <span>{{ sortOption.label }}</span>
                                    </v-list-item>
                                </template>
                            </v-list-item-group>
                        </v-list>
                    </FancyDropdown>
                    <ResourceExportBtn :partDict="partDict" :categories="categories" :searchQuery="searchQuery"
                        :supCount="count" />
                </div>
            </div>
            <div v-if="!isLoading">
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
                                        item.descriptionHeadline ||
                                        item.description
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
                                <span v-if="item.locations.length > 1"
                                    >§§
                                </span>
                                <span v-else>§ </span>
                                <template
                                    v-for="(location, i) in item.locations"
                                >
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
                                        <span
                                            v-if="
                                                i + 1 != item.locations.length
                                            "
                                        >
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
        </div>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";
import FancyDropdown from "@/components/custom_elements/FancyDropdown.vue";
import SearchEmptyState from "@/components/SearchEmptyState.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import ResourceExportBtn from "@/components/resources/ResourceExportBtn.vue";

const SORT_METHODS = {
    newest: "Date (Newest)",
    oldest: "Date (Oldest)",
    relevance: "Relevance",
};

export default {
    name: "ResourcesResults",

    components: {
        FancyDropdown,
        SearchEmptyState,
        SupplementalContentObject,
        ResourceExportBtn,
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

    props: {
        content: {
            type: Array,
            required: false,
            default() {
                return [];
            },
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
        count: {
            type: Number,
            required: false,
            default: 0,
        },
        isLoading: {
            type: Boolean,
            required: false,
            default: false,
        },
        partsList: {
            type: Array,
            required: true,
            default: () => [],
        },
        partsLastUpdated: {
            type: Object,
            required: true,
            default: () => {},
        },
        query: {
            type: String,
            required: false,
            default: "",
        },
        sortMethod: {
            validator: (value) => Object.keys(SORT_METHODS).includes(value),
            required: false,
            default: "newest",
        },
        sortDisabled: {
            type: Boolean,
            required: false,
            default: false,
        },
        disabledSortOptions: {
            type: Array,
            required: false,
            default() {
                return [];
            },
        },
    },

    data() {
        return {
            activeSortMethod: this.sortMethod,
            base:
                import.meta.env.VITE_ENV && import.meta.env.VITE_ENV !== "prod"
                    ? `/${import.meta.env.VITE_ENV}`
                    : "",
        };
    },

    computed: {
        regulationsSearchUrl() {
            return `${this.base}/search/`;
        },
        filteredContent() {
            return this.content.map((item) => {
                const copiedItem = JSON.parse(JSON.stringify(item));
                copiedItem.locations = item.locations.filter(
                    (location) => this.partsLastUpdated[location.part]
                );
                return copiedItem;
            });
        },
        sortMethodTitle() {
            return SORT_METHODS[this.sortMethod];
        },
        sortOptions() {
            return Object.keys(SORT_METHODS).map((key) => ({
                label: SORT_METHODS[key],
                value: key,
                disabled: this.disabledSortOptions.includes(key),
            }));
        },
        currentPageResultsRange() {
            const maxInRange = this.page * this.pageSize;
            const minInRange = maxInRange - this.pageSize;

            const firstInRange = minInRange + 1;
            const lastInRange =
                maxInRange > this.count
                    ? (this.count % this.pageSize) + minInRange
                    : maxInRange;

            return [firstInRange, lastInRange];
        },
    },

    methods: {
        clickMethod(e) {
            this.$emit("sort", e.currentTarget.dataset.value);
        },
    },
};
</script>

<style lang="scss">
.results-container {
    overflow: auto;
    width: 100%;
    margin-bottom: 30px;

    .results-content {
        max-width: $text-max-width;
        margin: 0 auto;

        .top-rule {
            border-top: 1px solid #dddddd;
            margin-bottom: 30px;
        }

        .results-count {
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sort-control {
            display: flex;
            align-items: center;
            font-weight: normal;

            div:first-of-type {
                width: 140px;
            }

            @include custom-max($mobile-max / 1px) {
                .sort-control-label {
                    margin-right: 9px;
                }
            }
        }

        .category-labels {
            margin-bottom: 5px;

            .result-label {
                font-size: 11px;
                display: inline;
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
                    font-size: 18px;
                }
            }
        }

        .related-sections {
            margin-bottom: 40px;
            font-size: 12px;
            color: $mid_gray;

            .related-sections-title {
                font-weight: 600;
                color: $dark_gray;
            }

            a {
                text-decoration: none;
            }
        }
    }
}
</style>
