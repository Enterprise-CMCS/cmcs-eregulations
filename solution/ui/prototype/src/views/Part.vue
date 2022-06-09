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
                        v-for="item in tabsShape"
                        :key="item.label"
                        :disabled="item.disabled"
                    >
                        {{ item.label }}
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
                                ></component>
                            </FancyDropdown>
                        </template>
                    </v-tab>
                </v-tabs>
            </PartNav>
            <div class="content-container content-container-sidebar">
                <v-tabs-items v-model="tab">
                    <v-tab-item v-for="(item, index) in tabsShape" :key="index">
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
import SectionResourcesSidebar from "@/components/SectionResourcesSidebar.vue";
import SubpartList from "@/components/custom_elements/SubpartList.vue";
import SectionList from "@/components/custom_elements/SectionList.vue";

import {
    getPart,
    getSubPartsForPart,
    getSupplementalContentCountForPart,
} from "@/utilities/api";

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
        SubpartList,
        SectionList,
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            tabParam: this.$route.params.tab,
            structure: null,
            sections: [],
            tabsShape: [
                {
                    label: "Table of Contents",
                    value: "tocContent",
                    type: "button",
                    component: "PartToc",
                    disabled: false,
                },
                {
                    label: "Part",
                    value: "partContent",
                    type: "button",
                    component: "PartContent",
                    disabled: false,
                },
                {
                    label: "Subpart",
                    value: "subpart",
                    listType: "SubpartList",
                    type: "dropdown",
                    disabled: false,
                    listItems: [],
                },
                {
                    label: "Section",
                    value: "section",
                    listType: "SectionList",
                    type: "dropdown",
                    disabled: false,
                    listItems: [],
                },
            ],
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
                switch (value) {
                    case 0:
                        this.$router.push({
                            name: "part",
                            params: {
                                title: this.title,
                                part: this.part,
                                tab: "toc",
                            },
                        });
                        break;
                    case 1:
                        this.$router.push({
                            name: "part",
                            params: {
                                title: this.title,
                                part: this.part,
                                tab: "part",
                            },
                        });
                        break;
                    case 2:
                        this.$router.push({
                            name: "part",
                            params: {
                                title: this.title,
                                part: this.part,
                                tab: "subpart",
                            },
                        });
                        break;
                    case 3:
                        this.$router.push({
                            name: "part",
                            params: {
                                title: this.title,
                                part: this.part,
                                tab: "section",
                            },
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
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
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
            }
        );

        await this.getPartStructure();
        await this.getFormattedSubpartsList(this.part);
    },

    methods: {
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
            console.log("payload", payload);
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
        async getFormattedSubpartsList(part) {
            const formattedSubpartsList = await getSubPartsForPart(part);
            const tabIndex = this.tabsShape.findIndex(
                (tab) => tab.value === "subpart"
            );
            this.tabsShape[tabIndex].listItems = formattedSubpartsList;
        },
    },

    watch: {
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
