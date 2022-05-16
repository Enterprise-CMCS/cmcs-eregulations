<template>
    <div id="app" class="resources-view">
        <ResourcesNav :resourcesDisplay="resourcesDisplay" :aboutUrl="aboutUrl">
            <form class="search-resources-form" @submit.prevent="executeSearch">
                <v-text-field
                    outlined
                    flat
                    solo
                    clearable
                    label="Search Resources"
                    type="text"
                    class="search-field"
                    append-icon="mdi-magnify"
                    hide-details
                    dense
                    v-model="searchInputValue"
                    @click:append="executeSearch"
                    @click:clear="clearSearchQuery"
                >
                </v-text-field>
            </form>
        </ResourcesNav>
        <div
            class="resources-content-container"
            :class="contentContainerResourcesClass"
        >
            <div :class="filtersResourcesClass">
                <ResourcesFilters
                    :resourcesDisplay="resourcesDisplay"
                    :filters="filters"
                    @select-filter="updateFilters"
                />
            </div>
            <div :class="resultsResourcesClass">
                <ResourcesSelections
                    :filterParams="filterParams"
                    @chip-filter="removeChip"
                    @clear-selections="clearSelections"
                />
                <ResourcesResults
                    :isLoading="isLoading"
                    :content="supplementalContent"
                    :partsList="filters.part.listItems"
                    :partsLastUpdated="partsLastUpdated"
                />
            </div>
        </div>
    </div>
</template>

<script>
import {
    getAllParts,
    getCategories,
    getLastUpdatedDates,
    getSectionObjects,
    getSubPartsForPart,
    getSupplementalContentNew,
} from "legacy/js/api";

import ResourcesNav from "@/components/resources/ResourcesNav.vue";
import ResourcesFilters from "@/components/resources/ResourcesFilters.vue";
import ResourcesSelections from "@/components/resources/ResourcesSelections.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";

import _difference from "lodash/difference";
import _isEmpty from "lodash/isEmpty";
import _uniq from "lodash/uniq";

export default {
    name: "Resources",

    components: {
        ResourcesNav,
        ResourcesFilters,
        ResourcesSelections,
        ResourcesResults,
    },

    props: {
        apiUrl: {
            type: String,
            default: "/v2/",
        },
        aboutUrl: {
            type: String,
            default: "/about/",
        },
    },

    data() {
        return {
            isLoading: false,
            queryParams: this.$route.query,
            resourcesDisplay: "column",
            partsLastUpdated: {},
            filters: {
                part: {
                    label: "Part",
                    buttonTitle: "Select Parts",
                    buttonId: "select-parts",
                    listType: "TitlePartList",
                    listItems: [],
                },
                subpart: {
                    label: "Subpart",
                    buttonTitle: "Select Subparts",
                    buttonId: "select-subparts",
                    listType: "SubpartList",
                    listItems: [],
                },
                section: {
                    label: "Section",
                    buttonTitle: "Select Sections",
                    buttonId: "select-sections",
                    listType: "SectionList",
                    listItems: [],
                },
                resourceCategory: {
                    label: "Resource Category",
                    buttonTitle: "Select Categories",
                    buttonId: "select-resource-categories",
                    listType: "CategoryList",
                    listItems: [],
                },
            },
            supplementalContent: [],
            searchInputValue: "",
        };
    },

    computed: {
        contentContainerResourcesClass() {
            return `resources-content-container-${this.resourcesDisplay}`;
        },
        filtersResourcesClass() {
            return `filters-${this.resourcesDisplay}`;
        },
        resultsResourcesClass() {
            return `results-${this.resourcesDisplay}`;
        },
        searchQuery: {
            get() {
                return this.queryParams.q || "";
            },
            set(value) {
                this.searchInputValue = value;
            },
        },
        filterParams() {
            return {
                title: this.queryParams.title,
                part: this.queryParams.part,
                subpart: this.queryParams.subpart,
                section: this.queryParams.section,
                resourceCategory: this.queryParams.resourceCategory,
            };
        },
    },

    methods: {
        executeSearch() {
            this.$router.push({
                name: "resources",
                query: {
                    ...this.filterParams,
                    q: this.searchInputValue,
                },
            });
        },
        clearSelections() {
            this.$router.push({
                name: "resources",
                query: {
                    title: undefined,
                    part: undefined,
                    subpart: undefined,
                    section: undefined,
                    resourceCategory: undefined,
                    q: this.searchQuery,
                },
            });
        },
        clearSearchQuery() {
            this.$router.push({
                name: "resources",
                query: { ...this.filterParams },
            });
        },
        removeChip(payload) {
            const newQueryParams = { ...this.queryParams };
            const scopeVals = newQueryParams[payload.scope].split(",");
            const newScopeVals = scopeVals.filter(
                (val) => val !== payload.selectedIdentifier
            );
            newQueryParams[payload.scope] = _isEmpty(newScopeVals)
                ? undefined
                : newScopeVals.join(",");
            if (_isEmpty(newQueryParams.part)) {
                newQueryParams.title = undefined;
                newQueryParams.subpart = undefined;
                newQueryParams.section = undefined;
            }
            this.$router.push({
                name: "resources",
                query: newQueryParams,
            });
        },
        updateFilters(payload) {
            const newQueryParams = { ...this.queryParams };
            if (newQueryParams[payload.scope]) {
                const scopeVals = newQueryParams[payload.scope].split(",");
                scopeVals.push(payload.selectedIdentifier);
                const uniqScopeVals = _uniq(scopeVals);
                newQueryParams[payload.scope] = uniqScopeVals.sort().join(",");
            } else {
                newQueryParams.title = "42"; // hard coding for now
                newQueryParams[payload.scope] = payload.selectedIdentifier;
            }
            this.$router.push({
                name: "resources",
                query: newQueryParams,
            });
        },
        filterCategories(resultArray) {
            const filteredArray = resultArray.filter((item) => {
                if (this.queryParams.resourceCategory.includes(item.name)) {
                    return true;
                }
            });

            return filteredArray;
        },
        transformResults(results, flatten) {
            const arrayToTransform = flatten ? results.flat() : results;
            let returnArr = [];

            for (const category of arrayToTransform) {
                returnArr = returnArr.concat(category);
                for (const subcategory of category.sub_categories) {
                    subcategory.parent_category = category.name;
                    returnArr = returnArr.concat(subcategory);
                }
            }

            return returnArr;
        },
        async getSupplementalContent(dataQueryParams, searchQuery) {
            this.isLoading = true;
            if (dataQueryParams?.part) {
                const queryParamsObj = { ...dataQueryParams };
                queryParamsObj.part = queryParamsObj.part.split(",");
                if (queryParamsObj.section) {
                    queryParamsObj.sections = queryParamsObj.section.split(",");
                }
                if (queryParamsObj.subpart) {
                    queryParamsObj.subparts = queryParamsObj.subpart.split(",");
                }
                // map over parts and return promises to put in Promise.all
                const partPromises = queryParamsObj.part.map((part) => {
                    return getSupplementalContentNew(
                        this.apiUrl,
                        42,
                        part,
                        queryParamsObj.sections,
                        queryParamsObj.subparts,
                        0, // start
                        10000, // max_results
                        searchQuery
                    );
                });

                try {
                    const resultArray = await Promise.all(partPromises);

                    const transformedResults = this.transformResults(
                        resultArray,
                        true
                    );

                    this.supplementalContent = this.queryParams.resourceCategory
                        ? this.filterCategories(transformedResults)
                        : transformedResults;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                } finally {
                    this.isLoading = false;
                }
            } else if (searchQuery) {
                try {
                    const searchResults = await getSupplementalContentNew(
                        this.apiUrl,
                        "all", // titles
                        "all", // parts
                        [], // sections
                        [], // subparts
                        0, // start
                        10000, // max_results
                        searchQuery
                    );

                    const transformedResults = this.transformResults(
                        searchResults,
                        false
                    );

                    this.supplementalContent = this.queryParams.resourceCategory
                        ? this.filterCategories(transformedResults)
                        : transformedResults;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                } finally {
                    this.isLoading = false;
                }
            } else {
                this.supplementalContent = [];
                this.isLoading = false;
            }
        },
        async getPartLastUpdatedDates() {
            this.partsLastUpdated = await getLastUpdatedDates(this.apiUrl);
        },
        async getFormattedPartsList() {
            const partsList = await getAllParts(this.apiUrl);
            this.filters.part.listItems = partsList.map((part) => {
                // get section parent (subpart) if exists.
                // this will be included in response in v3 api
                const sectionsArr = part.structure.children[0].children[0].children[0].children
                    .map(
                        (subpart) => {
                            if (_isEmpty(subpart.children)) return [];

                            const returnArray = subpart.children
                                ? subpart.children.map((section) => ({
                                      [section.identifier[1] ??
                                      section.identifier[0]]: section.parent[0],
                                  }))
                                : [{ [subpart.identifier[1]]: "orphan" }];
                            return returnArray;
                        }
                    )
                    .filter((section) => !_isEmpty(section))
                    .flat();
                return {
                    name: part.name,
                    label:
                        part.structure.children[0].children[0].children[0]
                            .label,
                    sections: Object.assign({}, ...sectionsArr),
                };
            });
        },
        async getFormattedSubpartsList(part) {
            this.filters.subpart.listItems = await getSubPartsForPart(
                this.apiUrl,
                part
            );
        },
        async getFormattedSectionsList(part, subpart) {
            this.filters.section.listItems = await getSectionObjects(
                this.apiUrl,
                part,
                subpart
            );
        },
        async getCategoryList() {
            const rawCats = await getCategories(this.apiUrl);
            const reducedCats = rawCats
                .filter((item) => item.object_type === "category")
                .sort((a, b) =>
                    a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1
                )
                .reduce((acc, item) => {
                    acc[item.name] = item;
                    acc[item.name].subcategories = [];
                    return acc;
                }, {});
            rawCats.forEach((item) => {
                if (item.object_type === "subcategory") {
                    reducedCats[item.parent.name].subcategories.push(item);
                }
            });
            this.filters.resourceCategory.listItems = Object.values(
                reducedCats
            );
        },
    },

    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
            },
        },
        "$route.query": {
            async handler(toQueries, previousQueries) {
                this.queryParams = toQueries;
            },
        },
        queryParams: {
            // beware, some yucky code ahead...
            async handler(newParams, oldParams) {
                if (_isEmpty(newParams.part) && _isEmpty(newParams.q)) {
                    // only get content if a part is selected or there's a search query
                    // don't make supp content request here, but clear lists
                    this.filters.subpart.listItems = [];
                    this.filters.section.listItems = [];
                    this.supplementalContent = [];

                    return;
                }

                // always get content otherwise
                this.getSupplementalContent(this.queryParams, this.searchQuery);

                if (newParams.part) {
                    // logic for populating select dropdowns
                    if (_isEmpty(oldParams.part) && newParams.part) {
                        this.getFormattedSubpartsList(this.queryParams.part);
                        this.getFormattedSectionsList(
                            this.queryParams.part,
                            this.queryParams.subpart
                        );
                    } else if (
                        _isEmpty(oldParams.subpart) &&
                        newParams.subpart
                    ) {
                        this.getFormattedSectionsList(
                            this.queryParams.part,
                            this.queryParams.subpart
                        );
                    } else {
                        const oldParts = oldParams.part.split(",");
                        const newParts = newParams.part.split(",");

                        if (newParts.length > oldParts.length) {
                            const newPart = _difference(newParts, oldParts)[0];
                            this.getFormattedSubpartsList(newPart);
                            this.getFormattedSectionsList(
                                newPart,
                                this.queryParams.subpart
                            );
                        }
                    }
                }
            },
        },
    },

    beforeCreate() {},

    async created() {
        this.getPartLastUpdatedDates();
        this.getFormattedPartsList();
        this.getCategoryList();

        if (this.queryParams?.part || this.queryParams?.q) {
            if (this.queryParams?.q) {
                this.searchQuery = this.queryParams.q;
            }

            this.getSupplementalContent(this.queryParams, this.searchQuery);

            if (this.queryParams?.part) {
                this.getFormattedSubpartsList(this.queryParams.part);
                this.getFormattedSectionsList(
                    this.queryParams.part,
                    this.queryParams.subpart
                );
            }
        }
    },

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},
};
</script>

<style lang="scss">
#app.resources-view {
    display: flex;
    flex-direction: column;

    .resources-content-container {
        display: flex;
        flex-direction: column;
    }

    .resources-content-container-column {
        display: flex;
        flex-direction: column;
        flex: 1;
    }

    .resources-content-container-sidebar {
        display: flex;
        flex-direction: row;
    }

    .filters-sidebar {
        display: flex;
        flex: 0 0 430px;
        max-width: 430px;
    }

    .results-sidebar {
        flex: 1;
        padding: 40px 80px 0;
    }

    .search-resources-form {
        .search-field {
            width: calc(100% - 25px);
            height: 40px;
            margin-bottom: 50px;

            .v-input__icon.v-input__icon--append button {
                color: $mid_blue;
            }
        }
    }
}
</style>
