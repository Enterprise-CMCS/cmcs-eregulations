<template>
    <div class="results-container">
        <div class="results-content">
            <hr class="top-rule" />
            <div class="results-count">
                <span v-if="isLoading">Loading...</span>
                <span v-else>
                    <span v-if="count > 0">
                        {{ currentPageResultsRange[0] }} -
                        {{ currentPageResultsRange[1] }} of
                    </span>
                    {{ count }} result<span v-if="count != 1">s</span> in
                    Resources
                </span>
                <div class="sort-control">
                    <span id="resultsSortLabel" class="sort-control-label">
                        Sort by
                    </span>
                    <FancyDropdown
                        :button-title="sortMethodTitle"
                        :disabled="sortDisabled"
                        button-id="sortButton"
                        list-id="resultsSortLabel"
                    >
                        <v-list class="sort-options-list">
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
                        </v-list>
                    </FancyDropdown>
                    <ResourceExportBtn
                        :partDict="partDict"
                        :categories="categories"
                        :query="query"
                        :supCount="count"
                    />
                </div>
            </div>
            <template v-if="!isLoading">
                <ResourcesResults
                    :base="base"
                    :count="count"
                    :filtered-content="filteredContent"
                    :page="page"
                    :page-size="pageSize"
                    :parts-last-updated="partsLastUpdated"
                    :parts-list="partsList"
                    :query="query"
                />
            </template>
        </div>
    </div>
</template>

<script>
import FancyDropdown from "@/components/custom_elements/FancyDropdown.vue";
import ResourceExportBtn from "@/components/resources/ResourceExportBtn.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";

const SORT_METHODS = {
    newest: "Date (Newest)",
    oldest: "Date (Oldest)",
    relevance: "Relevance",
};

export default {
    name: "ResourcesResultsContainer",

    components: {
        FancyDropdown,
        ResourceExportBtn,
        ResourcesResults,
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
        partDict: {
            type: Object,
            required: false,
            default: () => {},
        },
        categories: {
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
    }
}
</style>
