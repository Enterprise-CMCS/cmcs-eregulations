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
                        :query="searchQuery"
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
    getCategories,
    getSubPartsForPart,
    getSupplementalContentV3,
    getLastUpdatedDates,
    getTOC,
    getPartTOC,
    getSectionsForPart,
    getSubpartTOC,
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
            URL: import.meta.env.VITE_API_URL,
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
            const sectionRegex = /^\d{2,3}\.(\d{1,4})$/;

            if (sectionRegex.test(this.searchInputValue)) {
                let payload = {
                    scope: "section",
                    selectedIdentifier: this.searchInputValue.replace(".", "-"),
                    searchSection: true,
                };
                this.updateFilters(payload);
            }
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
            let newQueryParams = { ...this.queryParams };
            const splitSection = payload.selectedIdentifier.split("-");

            //Checks that the part in the query is valid or is a resource category
            if ((await this.checkPart(splitSection, payload.scope)) || payload.scope == "resourceCategory") {
                if (newQueryParams[payload.scope]) {
                    if (payload.searchSection) {
                        if (!newQueryParams.part.includes(splitSection[0])) {
                            newQueryParams.part =
                                newQueryParams.part + "," + splitSection[0];
                        }
                    }
                    const scopeVals = newQueryParams[payload.scope].split(",");
                    scopeVals.push(payload.selectedIdentifier);
                    const uniqScopeVals = _uniq(scopeVals);
                    newQueryParams[payload.scope] = uniqScopeVals
                        .sort()
                        .join(",");
                } else {
                    newQueryParams.title = "42"; // hard coding for now
                    if (payload.scope === "section") {
                        if (newQueryParams.part) {
                            newQueryParams.part =
                                newQueryParams.part + "," + splitSection[0];
                        } else {
                            newQueryParams.part = splitSection[0];
                        }
                    }
                    newQueryParams[payload.scope] = payload.selectedIdentifier;
                }

                if (payload.scope === "subpart") {
                      newQueryParams = await this.combineSections(
                        payload.selectedIdentifier,
                        newQueryParams
                    );
                }

                if (payload.searchSection) {
                    newQueryParams.q = "";
                    this.searchInputValue = "";
                }

                this.getPartDict(newQueryParams)

                this.$router.push({
                    name: "resources",
                    query: newQueryParams,
                });
            }
        },

        async checkPart(payload, scope) {
            const partExist = this.filters.part.listItems.filter((part) => part.name == payload[0]).length > 0;

            if (partExist && scope === "section") {
                const sectionList = await getSectionsForPart(42, payload[0]);
                return sectionList.filter((section) => section.identifier[1] == payload[1]).length >0;
            }
            return partExist;
        },

        async combineSections(subpart, queryParams) {
            let sections = await this.getSectionsBySubpart(subpart);
            if (queryParams.section) {
                sections = _uniq(
                    queryParams.section.split(",").concat(sections)
                );
            }

            queryParams.section = sections.join(",");
            return queryParams;
        },
        async getSectionsBySubpart(subpart) {
            const splitSubpart = subpart.split("-");
            const allSections = await getSubpartTOC(
                42,
                splitSubpart[0],
                splitSubpart[1]
            );
            const sectionList = allSections
                .filter((sec) => sec.type === "section")
                .map((sec) => `${sec.identifier[0]}-${sec.identifier[1]}`);
            return sectionList;
        },
        filterCategories(resultArray) {
            return resultArray.filter((item) =>
                this.queryParams.resourceCategory.includes(item.name)
            );
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
        getPartDict(dataQueryParams) {
            const parts = dataQueryParams.part.split(",");
            const newPartDict = {};

            parts.forEach((x) => {
                newPartDict[x] = {
                    title: "42",
                    sections: [],
                    subparts: [],
                };
            });

            this.partDict = newPartDict;

            if (dataQueryParams.section) {
                const sections = dataQueryParams.section
                    .split(",")
                    .filter((x) => x.match(/^\d+/) && x.match(/\d+$/))
                    .map((x) => ({
                        part: x.match(/^\d+/)[0],
                        section: x.match(/\d+$/)[0],
                    }));
                Object.keys(sections).forEach((section) => {
                    this.partDict[sections[section].part].sections.push(
                        sections[section].section
                    );
                });
            }
            if (dataQueryParams.subpart) {
                const subparts = dataQueryParams.subpart
                    .split(",")
                    .filter((x) => x.match(/^\d+/) && x.match(/\w+$/))
                    .map((x) => ({
                        part: x.match(/^\d+/)[0],
                        subparts: x.match(/\w+$/)[0],
                    }));

                Object.keys(subparts).forEach((subpart) => {
                    this.partDict[subparts[subpart].part].subparts.push(
                        subparts[subpart].subparts
                    );
                });
            }
        },

        async getSupplementalContent(dataQueryParams, searchQuery) {
            this.isLoading = true;

            if (dataQueryParams.resourceCategory) {
                this.categories = dataQueryParams.resourceCategory.split(",");
            } else {
                this.categories = [];
            }
            if (dataQueryParams?.part) {
                this.getPartDict(dataQueryParams);
                // map over parts and return promises to put in Promise.all
                const partPromises = await getSupplementalContentV3({
                    partDict: this.partDict,
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
                        paginate: true,
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
                    paginate: false,
                });
                this.isLoading = false;
            }
        },
        async getFormattedPartsList() {
            const TOC = await getTOC();
            const partsList = TOC[0].children[0].children
                .map((subChapter) =>
                    subChapter.children.map((part) => ({
                        label: part.label,
                        name: part.identifier[0],
                    }))
                )
                .flat(1);

            this.filters.part.listItems = await Promise.all(
                partsList.map(async (part) => {
                    const newPart = JSON.parse(JSON.stringify(part));
                    const PartToc = await getPartTOC(42, part.name);
                    const sections = {};
                    PartToc.children
                        .filter((TOCpart) => TOCpart.type === "subpart")
                        .forEach((subpart) => {
                            subpart.children
                                .filter((section) => section.type === "section")
                                .forEach((c) => {
                                    sections[
                                        c.identifier[c.identifier.length - 1]
                                    ] = c.parent[0];
                                });
                        });
                    newPart.sections = sections;
                    return newPart;
                })
            );
        },

        async getFormattedSubpartsList(parts) {
            this.filters.subpart.listItems = await getSubPartsForPart(parts);
        },

        async getFormattedSectionsList() {
            const rawSections = await Promise.all(
                Object.keys(this.partDict).map(async (part) =>
                    getSectionsForPart("42", part)
                )
            );

            const finalSections = rawSections.flat(1).map((section) => ({
                label: section.label_level,
                description: section.label_description,
                part: section.identifier[0],
                [section.parent_type]: section.parent[0],
                identifier: section.identifier[section.identifier.length - 1],
            }));

            this.filters.section.listItems = finalSections
                .flat(1)
                .sort((a, b) =>
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

            const categories = Object.values(reducedCats).sort(
                (a, b) => a.order - b.order
            );
            categories.forEach((category) => {
                category.subcategories.sort((a, b) => a.order - b.order);
            });
            this.filters.resourceCategory.listItems = categories;
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

        if (this.queryParams.q) {
            this.searchQuery = this.queryParams.q;
        }

        if (this.queryParams.part) {
            this.getFormattedSubpartsList(this.queryParams.part);
            this.getFormattedSectionsList(
                this.queryParams.part,
                this.queryParams.subpart
            );
        }

        this.getSupplementalContent(this.queryParams, this.searchQuery);
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







