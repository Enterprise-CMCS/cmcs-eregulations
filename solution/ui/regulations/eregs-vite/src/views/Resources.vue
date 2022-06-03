<template>
    <body class="ds-base">
        <div id="app" class="resources-view">
            <ResourcesNav :aboutUrl="aboutUrl">
                <form
                    class="search-resources-form"
                    @submit.prevent="executeSearch"
                >
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
                    />

                </form>
            </ResourcesNav>
            <div
                class="resources-content-container"
                :class="contentContainerResourcesClass"
            >
                <div :class="filtersResourcesClass">
                    <ResourcesFilters
                        v-if="resourcesDisplay === 'column'"
                        :resourcesDisplay="resourcesDisplay"
                        :filters="filters"
                        @select-filter="updateFilters"
                    />
                    <ResourcesSidebarFilters
                        v-else
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
    </body>
</template>

<script>

import _isEmpty from "lodash/isEmpty";
import _uniq from "lodash/uniq";


import ResourcesNav from "@/components/resources/ResourcesNav.vue";
import ResourcesFilters from "@/components/resources/ResourcesFilters.vue";
import ResourcesSelections from "@/components/resources/ResourcesSelections.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";

import {
    getAllParts,
    getCategories,
    getSubPartsForPart,
    getAllSections,
    getSupplementalContentV3,
    getLastUpdatedDates,

} from "../utilities/api";

export default {
    name: "Resources",

    components: {
        ResourcesNav,
        ResourcesFilters,
        ResourcesSelections,
        ResourcesResults,
    },

    props: {
        aboutUrl: {
            type: String,
            default: "/about/",
        },
    },

    data() {
        return {
            isLoading: false,
            queryParams: this.$route.query,
            partsLastUpdated: {},
            partDict: {},
            categories: [],
            testSup: [],
            resourcesDisplay:
                this.$route.name === "resources-sidebar" ? "sidebar" : "column",
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
            URL: import.meta.env.VITE_API_URL
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
            this.partDict = {};
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

            if (payload.scope === "part") {
                if (newQueryParams.subpart) {
                    let sub = newQueryParams.subpart?.split(",");
                    newQueryParams.subpart = sub
                        .filter(
                            (subpart) =>
                                !subpart.includes(payload.selectedIdentifier)
                        )
                        .join(",");
                }

                if (newQueryParams.section) {
                    let sec = newQueryParams.section.split(",");

                    newQueryParams.section = sec
                        .filter(
                            (section) =>
                                !section.includes(payload.selectedIdentifier)
                        )
                        .join(",");
                }
            }

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

        async updateFilters(payload) {
            console.log(payload)
            let newQueryParams = { ...this.queryParams };

            if (newQueryParams[payload.scope]) {
                const scopeVals = newQueryParams[payload.scope].split(",");
                scopeVals.push(payload.selectedIdentifier);
                const uniqScopeVals = _uniq(scopeVals);
                newQueryParams[payload.scope] = uniqScopeVals.sort().join(",");
            } else {
                newQueryParams.title = "42"; // hard coding for now
                newQueryParams[payload.scope] = payload.selectedIdentifier;
            }
            if (payload.scope === "subpart") {
                newQueryParams = await this.combineSections(
                    payload.selectedIdentifier,
                    newQueryParams
                );

                this.getPartDict(newQueryParams);
            }
            this.$router.push({
                name: "resources",
                query: newQueryParams,
            });
        },

        async combineSections(subpart, queryParams) {
            let sections = await this.getSectionsBySubpart(subpart);
            if (queryParams["section"]) {
                sections = _uniq(
                    queryParams["section"].split(",").concat(sections)
                );
            }

            queryParams["section"] = sections.join(",");
            return queryParams;
        },
        async getSectionsBySubpart(subpart) {
            const splitSubpart = subpart.split("-");
            const allSections = await getAllSections();
            const sectionList = allSections
                .filter((sec) => {
                    return (
                        sec.part == splitSubpart[0] &&
                        sec.subpart == splitSubpart[1]
                    );
                })
                .map((sec) => sec.part + "-" + sec.identifier);

            return sectionList;
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
            let res = [];

            for (const r of this.testSup) {
                res = res.concat(r.results);
            }
            this.testSup = res;

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
        getPartDict(dataQueryParams) {

            const parts = dataQueryParams.part.split(",");
            const newPartDict = {}

            parts.forEach(x => {
                newPartDict[x] = {
                    title: "42",
                    sections: [],
                    subparts: [],
                };
            })

            this.partDict = newPartDict

            if (dataQueryParams.section) {
                let sections = dataQueryParams.section.split(",").map((x) => ({
                    part: x.match(/^\d+/)[0],
                    section: x.match(/\d+$/)[0],
                }));
                for (const section in sections) {
                    this.partDict[sections[section].part].sections.push(
                        sections[section].section
                    );
                }
            }
            if (dataQueryParams.subpart) {
                const subparts = dataQueryParams.subpart
                    .split(",")
                    .map((x) => {
                      console.log(x)
                      return ({
                        part: x.match(/^\d+/)[0],
                        subparts: x.match(/\w+$/)[0],
                        })
                    });

                for (const subpart in subparts) {
                    this.partDict[subparts[subpart].part].subparts.push(
                        subparts[subpart].subparts
                    );
                }
            }
            if (dataQueryParams.resourceCategory) {
               this.categories = dataQueryParams.resourceCategory.split(",");
            } else{
              this.categories = []
            }
        },

        async getSupplementalContent(dataQueryParams, searchQuery) {
            this.isLoading = true;

            if (dataQueryParams?.part) {
                this.getPartDict(dataQueryParams);

                // map over parts and return promises to put in Promise.all
                const partPromises = await getSupplementalContentV3({
                  partDict:this.partDict,
                  categories: this.categories,
                  q: searchQuery,
                });

                try {
                    this.supplementalContent = partPromises;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                } finally {
                    this.isLoading = false;
                }
            } else if (searchQuery) {
                try {
                    const searchResults = await getSupplementalContentV3({
                      partDict: "all", // titles
                      categories: this.categories, // subcategories
                      q: searchQuery,
                      paginate: true
                    });

                    this.supplementalContent = searchResults;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                } finally {
                    this.isLoading = false;
                }
            } else {
                this.supplementalContent = await getSupplementalContentV3({
                  partDict: "all", // titles
                  categories: this.categories,
                  q: searchQuery,
                  start: 0, // start
                  max_results: 100, // max_results
                  paginate:false,
                });
                this.isLoading = false;
            }
        },
        async getFormattedPartsList() {
            const partsList = await getAllParts(this.apiUrl);
            this.filters.part.listItems = partsList.map((part) => {
                // get section parent (subpart) if exists.
                // this will be included in response in v3 api
                const sectionsArr = part.structure.children[0].children[0].children[0].children
                    .map((subpart) => {
                        if (_isEmpty(subpart.children)) return [];
                        // handle mixed sections and subject_groups
                        const returnArray = subpart.children.map(
                            (subpartChild) => {
                                if (subpartChild.type === "section") {
                                    return {
                                        [subpartChild.identifier[1] ?? subpartChild.identifier[0]]:
                                        subpartChild.parent[0],
                                    };
                                }
                                // TODO: handle appendices with no children
                                if (_isEmpty(subpartChild.children)) return [];
                                return subpartChild.children.map((section) => ({
                                    [section.identifier[1] ?? section.identifier[0]]:
                                    subpartChild.parent[0],
                                }));
                            }
                        );
                        return returnArray;
                    })
                    .filter((section) => !_isEmpty(section))
                    .flat(2);
                return {
                    name: part.name,
                    label:
                        part.structure.children[0].children[0].children[0]
                            .label,
                    sections: Object.assign({}, ...sectionsArr),
                };
            });
        },

        async getFormattedSubpartsList(parts) {
            this.filters.subpart.listItems = await getSubPartsForPart(parts);
        },

        async getFormattedSectionsList() {
            const allSections = await getAllSections();

            let finalsSections = [];
            let sectionList = [];
            for (const part in this.partDict) {
                const sections = this.partDict[part].sections;
                const subparts = this.partDict[part].subparts;
                sectionList = allSections.filter((sec) => sec.part == part);
                if (subparts.length >0) {
                    sectionList = sectionList.filter((sec) => {
                        return (
                            subparts.includes(sec.subpart) ||
                            sections.includes(sec.identifier)
                        );
                    });
                }
                finalsSections = finalsSections.concat(sectionList);
            }
            this.filters.section.listItems = finalsSections.sort((a, b) =>
                a.part > b.part
                    ? 1
                    : a.part == b.part
                    ? parseInt(a.identifier) > parseInt(b.identifier)
                        ? 1
                        : -1
                    : -1
            );
        },
        async getPartLastUpdatedDates() {
            this.partsLastUpdated = await getLastUpdatedDates(this.apiUrl);
        },
        async getCategoryList() {
            const rawCats = await getCategories();
            const reducedCats = rawCats
                .filter((item) => item.type === "category")
                .reduce((acc, item) => {
                    acc[item.name] = item;
                    acc[item.name].subcategories = [];
                    return acc;
                }, {});

            rawCats.forEach((item) => {
                if (item.type === "subcategory") {
                    reducedCats[item.parent.name].subcategories.push(item);
                }
            });

            const categories = Object.values(reducedCats).sort((a, b) =>
                a.order - b.order
            );
            categories.forEach((category) => {
                category.subcategories.sort((a, b) =>
                    a.order - b.order
                );
            });
            this.filters.resourceCategory.listItems = categories
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
                if (
                    _isEmpty(newParams.part) &&
                    _isEmpty(newParams.q) &&
                    _isEmpty(newParams.resourceCategory)
                ) {
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
                        this.getFormattedSectionsList();
                    } else if (
                        _isEmpty(oldParams.subpart) &&
                        newParams.subpart
                    ) {
                        this.getFormattedSectionsList();
                    } else {
                        this.getFormattedSubpartsList(this.queryParams.part);
                        this.getFormattedSectionsList();
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
        } else {
            this.getSupplementalContent([], "");
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
    .results-column {
        padding: 0 $spacer-5;
        @include screen-xl {
            padding: 0 $spacer-4;
        }
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







