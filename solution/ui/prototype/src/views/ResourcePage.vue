<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <div class="searchpane">
                <v-text-field
                    flat
                    solo
                    clearable
                    class="search-bar"
                    label="Search"
                    type="text"
                    append-icon="mdi-magnify"
                    hide-details
                >
                </v-text-field>
            </div>
            <splitpanes>
                <pane min-size="30">
                    <div style="width: 100%; margin: 20px">
                        <ResourceFilters
                            :resourceParamsEmitter="setResourcesParams"
                        />
                    </div>
                </pane>
                <pane min-size="30">
                    <SectionPane v-bind:supList="sortedSupList" />
                </pane>
            </splitpanes>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import { Splitpanes, Pane } from "splitpanes";
import { getSupplementalContentNew } from "../utilities/api";
import "splitpanes/dist/splitpanes.css";
import ResourceFilters from "../components/ResourcesPage/ResourceFilters.vue";
import SectionPane from "../components/ResourcesPage/SectionSide.vue";
export default {
    name: "ResourcePage",
    components: {
        FlashBanner,
        Header,
        Footer,
        Splitpanes,
        Pane,
        ResourceFilters,
        SectionPane,
    },
    data: () => ({
        supList: [],
        filters: [],
        singleSupList: [],
        sortedSupList: [],
    }),
    methods: {
        setResourcesParams(payload) {
            this.filters = payload;

            this.sortedSupList = [];

            this.getSupContent();

            // Implement response to user choosing a section or subpart here
        },
        sortContent() {
            try {
                let i = 0;
                for (let content of this.singleSupList) {
                    if (
                        this.filters.resources.includes(content.name) ||
                        this.filters.resources.length == 0
                    ) {
                        if (content.supplemental_content.length > 0) {
                            for (let supplement of content.supplemental_content) {
                                supplement.category = content.name;
                                this.sortedSupList.push(supplement);
                            }
                        }
                        if (content.sub_categories.length > 0) {
                            for (let subcat of content.sub_categories) {
                                if (subcat.supplemental_content.length > 0) {
                                    for (let supplement of subcat.supplemental_content) {
                                        supplement.subcategory = subcat.name;
                                        supplement.category = content.name;
                                        this.sortedSupList.push(supplement);
                                    }
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                console.log("error");
            }
        },
        async getSupContent() {
            this.singleSupList = [];

            try {
                this.supList = [];
                for (let part in this.filters.parts) {
                    let query = this.filters.parts[part];

                    this.supList.push(
                        await getSupplementalContentNew(
                            42,
                            query["part"],
                            query["sections"],
                            query["subparts"]
                        )
                    );
                }
                for (let sup of this.supList) {
                    for (let content of sup) {
                        this.singleSupList.push(content);
                    }
                }
            } catch (error) {
                console.error(error);
            } finally {
                console.log(this.structure);
            }
            this.sortContent();
        },
    },
};
</script>
<style scoped>
.searchpane {
    width: 100%;
    height: 127px;
    background-color: #f3f3f3;
}

.search-bar.v-text-field.v-text-field--enclosed {
    max-width: 610px;

    height: 20px;
    box-sizing: border-box;
    margin: auto auto;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 40px;
    margin-bottom: 40px;
}
</style>

