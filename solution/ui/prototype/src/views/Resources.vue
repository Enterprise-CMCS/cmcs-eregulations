<template>
    <body class="ds-base">
        <div id="app" class="resources-view">
            <Header />
            <ResourcesNav :resourcesDisplay="resourcesDisplay">
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
                    />
                </div>
            </div>
        </div>
    </body>
</template>

<script>
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import ResourcesNav from "@/components/resources/ResourcesNav.vue";
import ResourcesFilters from "@/components/resources/ResourcesFilters.vue";
import ResourcesSidebarFilters from "@/components/resources/ResourcesSidebarFilters.vue";
import ResourcesSelections from "@/components/resources/ResourcesSelections.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";

import _difference from "lodash/difference";
import _isEmpty from "lodash/isEmpty";
import _uniq from "lodash/uniq";

import {
    getAllParts,
    getCategories,
    getSectionObjects,
    getSubPartsForPart,
    getAllSections,
    getSupplementalContentV3,
    getSupplementalContentNew,
} from "@/utilities/api";

export default {
    name: "Resources",

    components: {
        Footer,
        Header,
        ResourcesNav,
        ResourcesFilters,
        ResourcesSidebarFilters,
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
                console.log(newQueryParams)
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
            console.log(dataQueryParams)
            const parts = dataQueryParams.part.split(",");

            for (const x in parts) {
                this.partDict[parts[x]] = {
                    title: "42",
                    sections: [],
                    subparts: [],
                };
            }

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
                    .map((x) => ({
                        part: x.match(/^\d+/)[0],
                        subparts: x.match(/\w+$/)[0],
                    }));

                for (const subpart in subparts) {
                    this.partDict[subparts[subpart].part].subparts.push(
                        subparts[subpart].subparts
                    );
                }
            }
            if (dataQueryParams.resourceCategory) {
               this.categories = dataQueryParams.resourceCategory.split(",");
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
                  fr_grouping: true,
                });

                try {
                    console.log(partPromises)
                    this.supplementalContent = partPromises;
                    console.log(this.supplementalContent)
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
                      categories: this.categories, //subcategories
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
                  categories: this.filterParams.resourceCategory ? this.filterParams.resourceCategory.split(",") : "", //subcategories
                  q: searchQuery,
                  start: 0, // start
                  max_results: 100, // max_results
                  paginate:false,
                });
                this.isLoading = false;
            }
        },
        async getFormattedPartsList() {
            const partsList = await getAllParts();

            this.filters.part.listItems = partsList.map((part) => {
                return {
                    name: part.name,
                    label: part.structure.children[0].children[0].children[0]
                        .label,
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
                console.log(this.partDict)
                const sections = this.partDict[part].sections;
                const subparts = this.partDict[part].subparts;
                console.log(part)
                console.log(allSections)
                sectionList = allSections.filter((sec) => sec.part == part);
                console.log(sectionList)
                console.log(subparts)
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
            console.log('dkfjd')
            console.log(finalsSections)
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

        async getCategoryList() {
            const rawCats = await getCategories();
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
            this.filters.resourceCategory.listItems =
                Object.values(reducedCats);
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
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

$sidebar-top-margin: 40px;

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
