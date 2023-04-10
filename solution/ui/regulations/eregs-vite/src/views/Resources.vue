<template>
    <body class="ds-base">
        <BlockingModal where-used="vite">
            <IFrameContainer
                src="https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
                title="Google Forms iframe"
            />
        </BlockingModal>
        <FlashBanner />
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :about-url="aboutUrl"
                        :resources-url="resourcesUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="resourcesApp" class="resources-view">
            <Banner title="Resources">
                <template #description>
                    <p>
                        Find public documents related to policy research,
                        including proposed and final rules published
                        <a
                            href="https://www.federalregister.gov/agencies/centers-for-medicare-medicaid-services"
                            target="_blank"
                            class="external"
                            >in the Federal Register</a
                        >
                        and subregulatory guidance and implementation resources
                        published
                        <a
                            href="https://www.medicaid.gov/federal-policy-guidance/index.html"
                            target="_blank"
                            class="external"
                            >by CMS</a
                        >.
                    </p>
                    <p>
                        <a :href="aboutUrl"
                            >How these links are added and connected to
                            regulation sections.</a
                        >
                    </p>
                </template>
                <template #input>
                    <form
                        class="search-resources-form"
                        @submit.prevent="executeSearch"
                    >
                        <v-text-field
                            id="main-content"
                            v-model="searchInputValue"
                            outlined
                            flat
                            solo
                            clearable
                            label="Search resources using keywords or citations."
                            aria-label="Search resources using keywords or citations."
                            type="text"
                            class="search-field"
                            append-icon="mdi-magnify"
                            hide-details
                            dense
                            @click:append="executeSearch"
                            @click:clear="clearSearchQuery"
                        />
                        <div
                            v-if="synonyms.length > 0 || multiWordQuery"
                            class="search-suggestion"
                        >
                            <div v-if="multiWordQuery">
                                Didn't find what you were looking for? Try
                                searching for
                                <a
                                    tabindex="0"
                                    @click="doQuoteSearch"
                                    @keydown.enter.space.prevent="doQuoteSearch"
                                    >"{{ searchQuery }}"</a
                                >
                            </div>
                            <div v-if="synonyms.length > 0" class="synonyms">
                                <span v-if="multiWordQuery">Or s</span
                                ><span v-else>S</span>earch for similar terms:
                                <span v-for="a in synonyms" :key="a">
                                    <a
                                        tabindex="0"
                                        @click="synonymLinks(a)"
                                        @keydown.enter.space.prevent="
                                            synonymLinks(a)
                                        "
                                        >{{ a }}</a
                                    >
                                    <span
                                        v-if="
                                            synonyms[synonyms.length - 1] != a
                                        "
                                        >,
                                    </span>
                                </span>
                            </div>
                        </div>
                    </form>
                </template>
            </Banner>
            <div
                class="resources-content-container resouces-content-container-column"
            >
                <div class="filters-column">
                    <ResourcesFilters
                        :filters="filters"
                        @select-filter="updateFilters"
                    >
                        <template #chips>
                            <ResourcesSelections
                                :filter-params="filterParams"
                                @chip-filter="removeChip"
                                @clear-selections="clearSelections"
                            />
                        </template>
                    </ResourcesFilters>
                </div>
                <div class="results-column">
                    <ResourcesResultsContainer
                        :isLoading="isLoading"
                        :base="homeUrl"
                        :page="page"
                        :page-size="pageSize"
                        :categories="categories"
                        :content="supplementalContent"
                        :count="supplementalContentCount"
                        :partsList="filters.part.listItems"
                        :partsLastUpdated="partsLastUpdated"
                        :query="searchQuery"
                        :sortMethod="sortMethod"
                        :disabledSortOptions="disabledSortOptions"
                        :sortDisabled="sortDisabled"
                        :partDict="partDict"
                        @sort="setSortMethod"
                    />
                </div>
            </div>
        </div>
    </body>
</template>

<script>
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";
import _uniq from "lodash/uniq";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import Banner from "@/components/Banner.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import JumpTo from "@/components/JumpTo.vue";
import ResourcesFilters from "@/components/resources/ResourcesFilters.vue";
import ResourcesSelections from "@/components/resources/ResourcesSelections.vue";
import ResourcesResultsContainer from "@/components/resources/ResourcesResultsContainer.vue";

import {
    getCategories,
    getFormattedPartsList,
    getLastUpdatedDates,
    getSectionsForPart,
    getSubPartsForPart,
    getSubpartTOC,
    getSupplementalContent,
    getSynonyms,
    getTitles,
} from "@/utilities/api";

const DEFAULT_TITLE = "42";

export default {
    name: "ResourcesView",

    components: {
        Banner,
        BlockingModal,
        FlashBanner,
        HeaderComponent,
        HeaderLinks,
        HeaderSearch,
        IFrameContainer,
        JumpTo,
        ResourcesFilters,
        ResourcesSelections,
        ResourcesResultsContainer,
    },

    props: {
        aboutUrl: {
            type: String,
            default: "/about/",
        },
        customUrl: {
            type: String,
            default: "",
        },
        homeUrl: {
            type: String,
            default: "/",
        },
        resourcesUrl: {
            type: String,
            default: "/resources/",
        },
        searchUrl: {
            type: String,
            default: "/search/",
        },
        host: {
            type: String,
            default: "",
        },
    },

    data() {
        return {
            isLoading: true,
            queryParams: this.$route.query,
            partsLastUpdated: {},
            partDict: {},
            categories: [],
            synonyms: [],
            filters: {
                title: {
                    label: "Title",
                    buttonTitle: "Select Title",
                    buttonId: "select-title",
                    listType: "TitleList",
                    listItems: [],
                },
                part: {
                    label: "Part",
                    buttonTitle: "Select Parts",
                    buttonId: "select-parts",
                    listType: "PartList",
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
            supplementalContentCount: 0,
            searchInputValue: undefined,
            sortDisabled: false,
            pageSize: "100",
        };
    },

    computed: {
        page() {
            return _isUndefined(this.queryParams.page)
                ? this.queryParams.page
                : parseInt(this.queryParams.page, 10);
        },
        searchQuery: {
            get() {
                return this.queryParams.q || undefined;
            },
            set(value) {
                this.searchInputValue = value;
            },
        },
        multiWordQuery() {
            if (this.searchQuery === undefined) return false;

            return (
                this.searchQuery.split(" ").length > 1 &&
                this.searchQuery[0] !== '"' &&
                this.searchQuery[this.searchQuery.length - 1] !== '"'
            );
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
        sortMethod() {
            return this.queryParams.sort || "newest";
        },
        disabledSortOptions() {
            return _isEmpty(this.searchQuery) ? ["relevance"] : [];
        },
    },

    methods: {
        async executeSearch() {
            const sectionRegex = /^\d{2,3}\.(\d{1,4})$/;
            if (sectionRegex.test(this.searchInputValue)) {
                const payload = {
                    scope: "section",
                    selectedIdentifier: this.searchInputValue.replace(".", "-"),
                    searchSection: true,
                };
                this.updateFilters(payload);
            } else {
                this.$router.push({
                    name: "resources",
                    query: {
                        ...this.filterParams,
                        q: this.searchInputValue,
                        sort: this.sortMethod,
                    },
                });
            }
            this.synonyms = await this.retrieveSynonyms(this.searchInputValue);
        },
        clearSelections() {
            this.partDict = {};
            this.$router.push({
                name: "resources",
                query: {
                    q: this.searchQuery,
                    sort: this.sortMethod,
                },
            });
        },
        async synonymLinks(synonym) {
            this.searchInputValue = `"${synonym}"`;
            await this.executeSearch();
        },
        clearSearchQuery() {
            this.synonyms = [];
            this.$router.push({
                name: "resources",
                query: {
                    ...this.queryParams,
                    page: undefined,
                    q: undefined,
                },
            });
        },
        doQuoteSearch() {
            this.searchInputValue = `"${this.searchInputValue}"`;
            this.$router.push({
                name: "resources",
                query: {
                    ...this.queryParams,
                    page: undefined,
                    q: `"${this.searchQuery}"`,
                },
            });
        },

        removeChip(payload) {
            const newQueryParams = { ...this.queryParams, page: undefined };
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
        async retrieveSynonyms(query) {
            if (
                query &&
                query.charAt(0) == '"' &&
                query.charAt(query.length - 1) == '"'
            ) {
                query = query.slice(1, -1);
            }
            let synonyms = await getSynonyms(query);
            synonyms = synonyms.map((word) =>
                word.synonyms
                    .filter((word) => word.isActive == true)
                    .map((word) => word.baseWord)
            )[0];
            return synonyms ? synonyms : [];
        },
        async updateFilters(payload) {
            console.log("update filters payload", payload);
            let newQueryParams = { ...this.queryParams, page: undefined };
            const splitSection = payload.selectedIdentifier.split("-");

            if (payload.scope === "title") {
                newQueryParams.title = payload.selectedIdentifier;
                this.$router.push({
                    name: "resources",
                    query: newQueryParams,
                });
            }

            //Checks that the part in the query is valid or is a resource category
            if (
                (await this.checkPart(splitSection, payload.scope)) ||
                payload.scope === "resourceCategory"
            ) {
                if (newQueryParams[payload.scope]) {
                    if (payload.searchSection) {
                        if (!newQueryParams.part.includes(splitSection[0])) {
                            newQueryParams.part =
                                newQueryParams.part + "," + splitSection[0];
                        }
                    }
                    const scopeVals = newQueryParams[payload.scope].split(",");
                    if (payload.scope === "resourceCategory") {
                        const cats = await this.getSubCategories(
                            payload.selectedIdentifier
                        );
                        cats.forEach((cat) => scopeVals.push(cat));
                    } else {
                        scopeVals.push(payload.selectedIdentifier);
                    }

                    const uniqScopeVals = _uniq(scopeVals);
                    newQueryParams[payload.scope] = uniqScopeVals
                        .sort()
                        .join(",");
                } else {
                    newQueryParams.title =
                        newQueryParams.title ?? DEFAULT_TITLE;
                    if (payload.scope === "section") {
                        if (newQueryParams.part) {
                            if (
                                !newQueryParams.part.includes(splitSection[0])
                            ) {
                                newQueryParams.part =
                                    newQueryParams.part + "," + splitSection[0];
                            }
                        } else {
                            newQueryParams.part = splitSection[0];
                        }
                    }
                    if (payload.scope === "resourceCategory") {
                        newQueryParams[payload.scope] = (
                            await this.getSubCategories(
                                payload.selectedIdentifier
                            )
                        ).join(",");
                    } else {
                        newQueryParams[payload.scope] =
                            payload.selectedIdentifier;
                    }
                }

                if (payload.scope === "subpart") {
                    newQueryParams = await this.combineSections(
                        payload.selectedIdentifier,
                        newQueryParams
                    );
                }

                if (payload.searchSection) {
                    newQueryParams.q = "";
                    this.searchInputValue = undefined;
                }
                if (newQueryParams.part) {
                    this.getPartDict(newQueryParams);
                }
                this.$router.push({
                    name: "resources",
                    query: newQueryParams,
                });
            }
        },

        async checkPart(payload, scope) {
            const partExist = this.filters.part.listItems.find(
                (part) => part.name === payload[0]
            );

            if (partExist && scope === "section") {
                const title = this.queryParams.title ?? DEFAULT_TITLE;
                const sectionList = await getSectionsForPart(title, payload[0]);
                return sectionList.find(
                    (section) => section.identifier[1] === payload[1]
                );
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
                this.queryParams.title ?? DEFAULT_TITLE,
                splitSubpart[0],
                splitSubpart[1]
            );
            const sectionList = allSections
                .filter((sec) => sec.type === "section")
                .map((sec) => `${sec.identifier[0]}-${sec.identifier[1]}`);
            // subject groups are a bit lower down the tree, need to look there too.
            const subjectGroupSections = allSections
                .filter((sec) => sec.type === "subject_group")
                .map((subjgrp) =>
                    subjgrp.children.map(
                        (sec) => `${sec.identifier[0]}-${sec.identifier[1]}`
                    )
                )
                .flat(1);
            return sectionList.concat(subjectGroupSections).sort();
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

            parts.forEach((part) => {
                newPartDict[part] = {
                    title: this.queryParams.title ?? DEFAULT_TITLE,
                    sections: [],
                    subparts: [],
                };
            });

            this.partDict = newPartDict;

            if (dataQueryParams.section) {
                const sections = dataQueryParams.section
                    .split(",")
                    .filter(
                        (section) =>
                            section.match(/^\d+/) && section.match(/\d+$/)
                    )
                    .map((section) => ({
                        part: section.match(/^\d+/)[0],
                        section: section.match(/\d+$/)[0],
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
                    .filter(
                        (section) =>
                            section.match(/^\d+/) && section.match(/\w+$/)
                    )
                    .map((section) => ({
                        part: section.match(/^\d+/)[0],
                        subparts: section.match(/\w+$/)[0],
                    }));

                Object.keys(subparts).forEach((subpart) => {
                    this.partDict[subparts[subpart].part].subparts.push(
                        subparts[subpart].subparts
                    );
                });
            }
        },

        async getSupplementalContent(dataQueryParams, searchQuery, sortMethod) {
            this.isLoading = true;

            if (dataQueryParams.resourceCategory) {
                this.categories = dataQueryParams.resourceCategory.split(",");
            } else {
                this.categories = [];
            }

            if (dataQueryParams?.part) {
                this.getPartDict(dataQueryParams);
                const responseContent = await getSupplementalContent({
                    page: this.page,
                    page_size: this.pageSize,
                    partDict: this.partDict,
                    categories: this.categories,
                    q: searchQuery,
                    fr_grouping: false,
                    sortMethod,
                });

                try {
                    this.supplementalContent = responseContent.results;
                    this.supplementalContentCount = responseContent.count;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                    this.supplementalContentCount = 0;
                } finally {
                    this.isLoading = false;
                }
            } else if (searchQuery) {
                try {
                    const searchResults = await getSupplementalContent({
                        page: this.page,
                        page_size: this.pageSize,
                        partDict: "all", // titles
                        categories: this.categories, // subcategories
                        q: searchQuery,
                        fr_grouping: false,
                        sortMethod,
                    });

                    this.supplementalContent = searchResults.results;
                    this.supplementalContentCount = searchResults.count;
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                    this.supplementalContentCount = 0;
                } finally {
                    this.isLoading = false;
                }
            } else {
                const allResults = await getSupplementalContent({
                    page: this.page,
                    page_size: this.pageSize,
                    partDict: "all", // titles
                    categories: this.categories,
                    q: searchQuery,
                    start: 0, // start
                    fr_grouping: false,
                    max_results: 100, // max_results
                    sortMethod,
                });
                this.supplementalContent = allResults.results;
                this.supplementalContentCount = allResults.count;
                this.isLoading = false;
            }
        },
        async getFormattedSubpartsList(parts, title) {
            this.filters.subpart.listItems = await getSubPartsForPart(
                parts,
                title
            );
        },

        async getFormattedSectionsList() {
            const rawSections = await Promise.all(
                Object.keys(this.partDict).map(async (part) =>
                    getSectionsForPart(
                        this.queryParams.title ?? DEFAULT_TITLE,
                        part
                    )
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
        async getSubCategories(selectedCategory) {
            const rawCats = await getCategories();
            const reducedCats = rawCats
                .filter((item) => item.type === "category")
                .reduce((acc, item) => {
                    acc[item.name] = item;
                    acc[item.name].subcategories = [item.name];
                    return acc;
                }, {});
            // Not a top level category, no need to continue
            if (!reducedCats[selectedCategory]) {
                return [selectedCategory];
            }
            rawCats.forEach((item) => {
                if (item.type === "subcategory") {
                    reducedCats[item.parent.name].subcategories.push(item.name);
                }
            });

            return reducedCats[selectedCategory].subcategories;
        },
        setSortMethod(payload) {
            this.$router.push({
                name: "resources",
                query: {
                    ...this.filterParams,
                    q:
                        this.searchInputValue === null // getting set to null somewhere...
                            ? undefined
                            : this.searchInputValue,
                    sort: payload,
                },
            });
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
                if (this.sortDisabled) {
                    this.sortDisabled = false;
                }

                if (
                    _isEmpty(newParams.part) &&
                    _isEmpty(newParams.q) &&
                    _isEmpty(newParams.resourceCategory) &&
                    _isEmpty(newParams.sort) &&
                    _isUndefined(newParams.page) &&
                    _isUndefined(newParams.title)
                ) {
                    // only get content if a part is selected or there's a search query
                    // don't make supp content request here, but clear lists
                    this.filters.subpart.listItems = [];
                    this.filters.section.listItems = [];
                    this.supplementalContent = [];
                    this.supplementalContentCount = 0;

                    return;
                }

                // always get content otherwise
                this.getSupplementalContent(
                    this.queryParams,
                    this.searchQuery,
                    this.sortMethod
                );
                if (newParams.part) {
                    // logic for populating select dropdowns
                    if (_isEmpty(oldParams.part) && newParams.part) {
                        this.getFormattedSubpartsList(
                            this.queryParams.part,
                            this.queryParams.title ?? DEFAULT_TITLE
                        );
                        this.getFormattedSectionsList();
                    } else if (
                        _isEmpty(oldParams.subpart) &&
                        newParams.subpart
                    ) {
                        this.getFormattedSectionsList();
                    } else {
                        this.getFormattedSubpartsList(
                            this.queryParams.part,
                            this.queryParams.title ?? DEFAULT_TITLE
                        );
                        this.getFormattedSectionsList();
                    }
                }
            },
        },
    },

    beforeCreate() {},

    async created() {
        this.getPartLastUpdatedDates();
        this.getCategoryList();
        this.filters.title.listItems = await getTitles();

        this.filters.part.listItems = await getFormattedPartsList(
            this.queryParams.title ?? DEFAULT_TITLE
        );

        if (this.queryParams.q) {
            this.searchQuery = this.queryParams.q;
            this.synonyms = await this.retrieveSynonyms(this.queryParams.q);
        }

        if (this.queryParams.part) {
            this.getFormattedSubpartsList(
                this.queryParams.part,
                this.queryParams.title ?? DEFAULT_TITLE
            );
            this.getFormattedSectionsList(
                this.queryParams.part,
                this.queryParams.subpart
            );
        }

        this.getSupplementalContent(
            this.queryParams,
            this.searchQuery,
            this.sortMethod
        );
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
#resourcesApp.resources-view {
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
        .search-suggestion {
            margin-top: -34px;
            margin-bottom: 34px;
            font-size: 14px;
        }
    }
}
</style>
