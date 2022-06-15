<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <PartNav
                :title="title"
                :part="part"
                :partLabel="partLabel"
                resourcesDisplay="sidebar"
            >
                <v-tabs
                    slider-size="5"
                    class="nav-tabs"
                    v-model="tab"
                    ref="tabs"
                >
                    <v-tab
                        v-for="(item, key, index) in tabsShape"
                        :key="item.label"
                        :disabled="item.disabled"
                    >
                        {{ tabLabels[key] }}
                        <template
                            v-if="
                                item.value === 'subpart' ||
                                item.value === 'section'
                            "
                        >
                            <FancyDropdown
                                label=""
                                buttonTitle=""
                                type="splitTab"
                            >
                                <component
                                    :is="item.listType"
                                    :listItems="item.listItems"
                                    :filterEmitter="setQueryParam"
                                ></component>
                            </FancyDropdown>
                        </template>
                    </v-tab>
                </v-tabs>
            </PartNav>
            <div class="content-container content-container-sidebar">
                <v-tabs-items v-model="tab">
                    <v-tab-item
                        :transition="false"
                        v-for="(item, key, index) in tabsShape"
                        :key="index"
                    >
                        <component
                            :is="item.component"
                            :structure="tabsContent[index]"
                            :title="title"
                            :part="part"
                            resourcesDisplay="sidebar"
                            :selectedIdentifier="selectedIdentifier"
                            :selectedScope="selectedScope"
                            :supplementalContentCount="supplementalContentCount"
                            @view-resources="setResourcesParams"
                        ></component>
                    </v-tab-item>
                </v-tabs-items>
                <div class="sidebar" v-show="tabParam !== 'toc'">
                    <SectionResourcesSidebar
                        :title="title"
                        :part="part"
                        :selectedIdentifier="selectedIdentifier"
                        :selectedScope="selectedScope"
                        :routeToResources="routeToResources"
                    />
                </div>
            </div>
            <Footer />
        </div>
    </body>
</template>

<script>
import FancyDropdown from "@/components/custom_elements/FancyDropdown.vue";
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import PartContent from "@/components/part/PartContent.vue";
import PartNav from "@/components/part/PartNav.vue";
import PartToc from "@/components/part/PartToc.vue";
import PartSubpart from "@/components/part/PartSubpart.vue";
import PartSection from "@/components/part/PartSection.vue";
import SectionResourcesSidebar from "@/components/SectionResourcesSidebar.vue";
import SubpartList from "@/components/custom_elements/SubpartList.vue";
import SectionList from "@/components/custom_elements/SectionList.vue";

import {
    getAllSections,
    getPart,
    getSupplementalContentCountForPart,
    getPartTOC,
    getSectionsForPart,
} from "@/utilities/api";

import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";
import {getSubpartTOC} from "../utilities/api";

export default {
    components: {
        SectionResourcesSidebar,
        FancyDropdown,
        FlashBanner,
        Footer,
        Header,
        PartContent,
        PartNav,
        PartToc,
        PartSubpart,
        PartSection,
        SubpartList,
        SectionList,
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            tabParam: this.$route.params.tab,
            queryParams: this.$route.query,
            structure: null,
            sections: [],
            tabsShape: {
                toc: {
                    label: "Table of Contents",
                    value: "tocContent",
                    type: "button",
                    component: "PartToc",
                    disabled: false,
                },
                part: {
                    label: "Part",
                    value: "partContent",
                    type: "button",
                    component: "PartContent",
                    disabled: false,
                },
                subpart: {
                    label: "Subpart",
                    value: "subpart",
                    listType: "SubpartList",
                    type: "dropdown",
                    component: "PartSubpart",
                    disabled: false,
                    listItems: [],
                },
                section: {
                    label: "Section",
                    value: "section",
                    listType: "SectionList",
                    type: "dropdown",
                    component: "PartSection",
                    disabled: false,
                    listItems: [],
                },
            },
            tabLabels: {
                toc: "Table of Contents",
                part: "Part",
                subpart: "Subpart",
                section: "Section",
            },
            selectedIdentifier: null,
            selectedScope: null,
            supplementalContentCount: {},
        };
    },

    computed: {
        tab: {
            get() {
                switch (this.tabParam) {
                    case "toc":
                        return 0;
                    case "part":
                        return 1;
                    case "subpart":
                        return 2;
                    case "section":
                        return 3;
                    default:
                        return 1;
                }
            },
            set(value) {
                const urlParams = {
                    title: this.title,
                    part: this.part,
                };
                const qParams = { ...this.queryParams };
                const valueType = Object.keys(this.tabsShape)[value];

                switch (valueType) {
                    case "toc":
                        this.$router.push({
                            name: "part",
                            params: {
                                ...urlParams,
                                tab: "toc",
                            },
                            query: qParams,
                        });
                        break;
                    case "part":
                        this.$router.push({
                            name: "part",
                            params: {
                                ...urlParams,
                                tab: "part",
                            },
                            query: qParams,
                        });
                        break;
                    case "subpart":
                        this.$router.push({
                            name: "part",
                            params: {
                                ...urlParams,
                                tab: "subpart",
                            },
                            query: _isUndefined(qParams[valueType])
                                ? {
                                      ...qParams,
                                      [valueType]:
                                          this.tabsShape[valueType].listItems[0]
                                              .identifier,
                                  }
                                : qParams,
                        });
                        break;
                    case "section":
                        const subpartSelection = _isEmpty(qParams)
                            ? {
                                  subpart:
                                      this.tabsShape.subpart.listItems[0]
                                          .identifier,
                              }
                            : {};

                        const sectionSelection = _isUndefined(
                            qParams[valueType]
                        )
                            ? {
                                  section:
                                      this.tabsShape.section.listItems[0]
                                          .identifier,
                              }
                            : {};
                        this.$router.push({
                            name: "part",
                            params: {
                                ...urlParams,
                                tab: "section",
                            },
                            query: _isUndefined(qParams[valueType])
                                ? {
                                      ...qParams,
                                      ...subpartSelection,
                                      ...sectionSelection,
                                  }
                                : qParams,
                        });
                        break;
                }
            },
        },
        tocContent() {
            return this.structure?.[0];
        },
        partLabel() {
            return this.structure?.[0].label_description ?? "N/A";
        },
        partContent() {
            return this.structure?.[1];
        },
        tabsContent() {
            return [this.tocContent, this.partContent, null, null];
        },
    },

    async created() {
        if (this.queryParams.subpart) {
            this.tabLabels.subpart = this.formatTabLabel("subpart");
        }

        if (this.queryParams.section) {
            this.tabLabels.section = this.formatTabLabel("section");
        }
        await this.getPartStructure();
        await this.getFormattedSubpartsList({title: this.title, part:this.part});
        await this.getFormattedSectionsList({
          title: this.title,
          part: this.part,
          subpart: this.queryParams.subpart
        });

        if (_isEmpty(this.queryParams)) {
            let paramsToSet = {};
            if (this.tabParam == "subpart") {
                paramsToSet = {
                    subpart: this.tabsShape.subpart.listItems[0].identifier,
                };
            }
            if (this.tabParam == "section") {
                paramsToSet = {
                    subpart: this.tabsShape.subpart.listItems[0].identifier,
                    section: this.tabsShape.section.listItems[0].identifier,
                };
            }
            this.$router.push({
                name: "part",
                params: {
                    title: this.title,
                    part: this.part,
                    tab: this.tabParam,
                },
                query: paramsToSet,
            });
        }
    },

    methods: {
        formatTabLabel(type) {
            switch (type) {
                case "subpart":
                    return this.queryParams.subpart
                        ? `Subpart ${this.queryParams.subpart}`
                        : "Subpart";
                    break;
                case "section":
                    return this.queryParams.section
                        ? `§ ${this.part}.${this.queryParams.section}`
                        : "Section";
                    break;
                default:
                    return "N/A";
                    break;
            }
        },
        setQueryParam(payload) {
            const valueToSet = payload.selectedIdentifier.split("-")[1];
            let updatedQueryParams = {};
            // get associated subpart for section
            if (payload.scope == "section") {
                const sectionSubpart = this.tabsShape.section.listItems.find(
                    (item) => {
                        return item.identifier == valueToSet;
                    }
                ).subpart;
                const subpartToSet = sectionSubpart == "none" ? {} : { subpart: sectionSubpart };
                updatedQueryParams = {
                    ...this.queryParams,
                    ...subpartToSet,
                    section: valueToSet,
                };
            } else {
                updatedQueryParams = {
                    ...this.queryParams,
                    [payload.scope]: valueToSet,
                };
            }

            this.$router.push({
                name: "part",
                params: {
                    title: this.title,
                    part: this.part,
                    tab: payload.scope,
                },
                query: updatedQueryParams,
            });
        },
        async getPartStructure() {
            try {
                this.structure = await getPart(this.title, this.part);
                this.supplementalContentCount =
                    await getSupplementalContentCountForPart(this.part);
            } catch (error) {
                console.error(error);
            } finally {
                console.log(this.structure);
            }
        },
        setResourcesParams(payload) {
            if (payload.scope === "rendered") {
                return;
            }
            this.selectedIdentifier = payload.identifier;
            this.selectedScope = payload.scope;
        },
        clearResourcesParams() {
            console.log("clear resource params");
            this.selectedIdentifier = null;
            this.selectedScope = null;
        },
        routeToResources() {
            const identifiers = this.selectedIdentifier.reduce((acc, item) => {
                acc[this.selectedScope]
                    ? (acc[this.selectedScope] += `,${this.part}-${item}`)
                    : (acc[this.selectedScope] = `${this.part}-${item}`);
                return acc;
            }, {});

            this.$router.push({
                name: "resources",
                query: {
                    title: this.title,
                    part: this.part,
                    ...identifiers,
                },
            });
        },
        async getFormattedSubpartsList({title, part}) {
            const partTOC = await getPartTOC(title, part)
            this.tabsShape.subpart.listItems = partTOC.children.filter(child => child.type ==="subpart").map(subpart => ({
              label: subpart.label,
              part: subpart.parent[0],
              identifier: subpart.identifier[0],
              range: subpart.descendant_range,
            }));
        },
        async getFormattedSectionsList({title, part, subpart}) {

            const allSections = await getSectionsForPart(title, part)
            const filteredSections = allSections
                .filter((section) =>
                  subpart ? section.parent_type === "subpart" && section.parent[0] === subpart : true)
                .map(section =>({
                  subpart:section.parent[0],
                  identifier: section.identifier[1],
                  label: section.label_level,
                  description: section.label_description,
                  part
            }));
            this.tabsShape.section.listItems = filteredSections;
        },
    },

    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
                if (toParams.tab !== previousParams.tab) {
                    this.tabParam = toParams.tab;
                }

                if (toParams.part !== previousParams.part) {
                    this.structure = null;
                    this.clearResourcesParams();
                    this.title = toParams.title;
                    this.part = toParams.part;
                }
            },
        },
        "$route.query": {
            async handler(toQueries, previousQueries) {
                this.queryParams = toQueries;
                if (toQueries.subpart !== previousQueries.subpart) {
                    this.tabLabels.subpart = this.formatTabLabel("subpart");
                    await this.getFormattedSectionsList({
                      title: this.title,
                      part: this.part,
                      subpart: toQueries.subpart
                    });

                    if (!_isUndefined(previousQueries.subpart)) {
                        this.$router.push({
                            name: "part",
                            params: {
                                title: this.title,
                                part: this.part,
                                tab: this.tabParam,
                            },
                            query: {
                                subpart: toQueries.subpart,
                            },
                        });
                    }
                }

                if (toQueries.section !== previousQueries.section) {
                    this.tabLabels.section = this.formatTabLabel("section");
                }
            },
        },
        async part(newPart) {
            await this.getPartStructure();
        },
    },

    updated() {
        this.$nextTick(function () {
            // call onResize to fix tab highlight misalignment bug
            // https://github.com/vuetifyjs/vuetify/issues/4733
            this.$refs.tabs && this.$refs.tabs.onResize();
        });
    },
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

#app {
    display: flex;
    flex-direction: column;
}

.content-container {
    display: flex;
    flex-direction: row;
}

.content-container-sidebar {
    justify-content: space-between;
}

.sidebar {
    position: -webkit-sticky;
    position: sticky;
    top: $header-height + $sidebar-top-margin;
    height: calc(100vh - #{$header-height} - #{$sidebar-top-margin});
    flex: 0 0 450px;
    margin: $sidebar-top-margin 0;
    padding: 0 25px;
    border-left: 1px solid $light_gray;
    overflow: scroll;
}
</style>
