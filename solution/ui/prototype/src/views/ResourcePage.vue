<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <div class="searchpane">
                <v-text-field
                    v-on:click:append="search"
                    v-on:keydown.enter="search"
                    v-model="searchQuery"
                    flat
                    solo
                    clearable
                    class="search-bar"
                    label="Search"
                    type="text"
                    append-icon="mdi-magnify"
                    hide-details
                    ref="search"
                />
            </div>
            <splitpanes>
                <pane min-size="30">
                    <div style="width: 100%; margin: 20px">
                        <ResourceFilters
                            :resourceParamsEmitter="setResourcesParams"
                            :preSelectedParts="preSelectedParts"
                            :preSelectedSections="preSelectedSections"
                        />
                    </div>
                </pane>
                <pane min-size="30">
                    <SectionPane v-bind:supList="sortedSupList" v-bind:usingSearch="usingSearch" v-bind:searchQuery="searchQuery"/>
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
import { getSupplementalContentNew, getAllSupplementalContentByPieces, getSupplementalContentSearchResults } from "../utilities/api";
import "splitpanes/dist/splitpanes.css";
import ResourceFilters from "../components/ResourcesPage/ResourceFilters.vue";
import SectionPane from "../components/ResourcesPage/SectionSide.vue";
export default {
    name: "ResourcePage",
    components: {
        Header,
        Footer,
        Splitpanes,
        Pane,
        ResourceFilters,
        SectionPane,
    },
    data: () => ({
        supList: [],
        filters: {resources:[]},
        singleSupList: [],
        sortedSupList: [],
        preSelectedSections:[],
        preSelectedParts: [],
        searchQuery: "",
        usingSearch: false,
    }),
    async created() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const part = urlParams.get('part')
            if (part){
                  this.filters["parts"] = {
                      [part]: {part}
                  }
                this.preSelectedParts.push(part)
                const subpart = urlParams.get('subPart') ? urlParams.get('subPart').split('-')[1] : null
                const section = urlParams.get('section')
                if(subpart) {
                  this.preSelectedSections.push({part, subpart})
                  this.filters["parts"][part]["subparts"] = [subpart]
                }
                if(section) {
                  this.preSelectedSections.push({part, section})
                  this.filters["parts"][part]["sections"] = [section]
                }
            }
            console.log(this.filters)
            if (this.filters.parts){
              await this.getSupContent();
            }else {
              this.supList = await getAllSupplementalContentByPieces(0, 100);
              for (let sup of this.supList) {
                this.singleSupList.push(sup);
              }

              this.sortContent()
            }
        } catch (error) {
            console.error(error);
        }
    },
    methods: {
        async search(event) {
            this.supList = [];
            this.singleSupList = [];
            this.sortedSupList = [];
            this.supList.push(await getSupplementalContentSearchResults(this.searchQuery));
            for (let sup of this.supList) {
                for (let content of sup) {
                    let clone = JSON.parse(JSON.stringify(content));
                    clone.category = clone.category.name; //rewrites cache if `content` used instead of `clone`
                    this.singleSupList.push(clone);
                    this.sortedSupList.push(clone);
                }
            }
            this.sortedSupList.filter(content => content.name)
            this.usingSearch = true;
        },
        setResourcesParams(payload) {
            this.filters = payload;

            this.sortedSupList = [];
            this.supList =[]
            this.getSupContent();

            // Implement response to user choosing a section or subpart here
        },
        sortContent() {
            try {
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
                                        supplement.category = subcat.name;
                                        this.sortedSupList.push(supplement);
                                    }
                                }
                            }
                        }
                    }
                this.sortedSupList.filter(content => content.name)
                }
            } catch (error) {
                console.log("error");
            }
        },
        async getSupContent() {
            this.usingSearch = false;
            this.singleSupList = [];
            console.log(this.filters)
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

