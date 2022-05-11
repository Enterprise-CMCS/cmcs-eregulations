<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <PartNav
                :title="title"
                :part="part"
                :partLabel="partLabel"
                :resourcesDisplay="resourcesDisplay"
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
                    </v-tab>
                </v-tabs>
            </PartNav>
            <div
                class="content-container"
                :class="contentContainerResourcesClass"
            >
                <v-tabs-items v-model="tab">
                    <v-tab-item v-for="(item, index) in tabsShape" :key="index">
                        <component
                            :is="item.component"
                            :structure="tabsContent[index]"
                            :title="title"
                            :part="part"
                            :resourcesDisplay="resourcesDisplay"
                            :selectedIdentifier="selectedIdentifier"
                            :selectedScope="selectedScope"
                            :supplementalContentCount="supplementalContentCount"
                            @view-resources="setResourcesParams"
                        ></component>
                    </v-tab-item>
                </v-tabs-items>
                <div class="sidebar" v-show="resourcesDisplay === 'sidebar'">
                    <SectionResourcesSidebar
                        :title="title"
                        :part="part"
                        :selectedIdentifier="selectedIdentifier"
                        :selectedScope="selectedScope"
                        :routeToResources="routeToResources"
                    />
                </div>
            </div>
            <SectionResources
                v-if="resourcesDisplay === 'drawer' && selectedIdentifier"
                :title="title"
                :part="part"
                :selectedIdentifier="selectedIdentifier"
                :selectedScope="selectedScope"
                :routeToResources="routeToResources"
                @close="clearResourcesParams"
            />
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import PartContent from "@/components/part/PartContent.vue";
import PartNav from "@/components/part/PartNav.vue";
import PartToc from "@/components/part/PartToc.vue";
import SectionResources from "@/components/SectionResources.vue";
import SectionResourcesSidebar from "@/components/SectionResourcesSidebar.vue";

import { getPart, getSupplementalContentCountForPart } from "@/utilities/api";

export default {
    components: {
        SectionResources,
        SectionResourcesSidebar,
        FlashBanner,
        Footer,
        Header,
        PartContent,
        PartNav,
        PartToc,
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            resourcesDisplay: this.$route.params.resourcesDisplay || "drawer",
            structure: null,
            sections: [],
            tab: 1, // index 1, "Part"
            tabsShape: [
                {
                    label: "Table of Contents",
                    value: "tocContent",
                    type: "button",
                    component: "PartToc",
                    disabled: true,
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
                    type: "dropdown",
                    disabled: true,
                },
                {
                    label: "Section",
                    value: "section",
                    type: "dropdown",
                    disabled: true,
                },
            ],
            selectedIdentifier: null,
            selectedScope: null,
            supplementalContentCount: {},
        };
    },

    computed: {
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
        contentContainerResourcesClass() {
            return `content-container-${this.resourcesDisplay}`;
        },
    },

    async created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
                if (toParams.part !== previousParams.part) {
                    this.structure = null;
                    this.clearResourcesParams();
                    this.title = toParams.title;
                    this.part = toParams.part;
                    this.resourcesDisplay =
                        toParams.resourcesDisplay || "drawer";
                }
            }
        );

        await this.getPartStructure();
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
            if (payload.scope === "rendered"){
              return
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

            const routeName =
                this.resourcesDisplay === "sidebar"
                    ? "resources-sidebar"
                    : "resources";

            this.$router.push({
                name: routeName,
                query: {
                    title: this.title,
                    part: this.part,
                    ...identifiers,
                },
            });
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

.content-container-drawer {
    justify-content: center;
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
