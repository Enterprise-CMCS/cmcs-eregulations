<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <splitpanes>
                <pane min-size="30">
                    <div style="width: 100%; margin: 20px">
                        <ResourceFilters
                            :resourceParamsEmitter="setResourcesParams"
                        />
                    </div>
                </pane>
                <pane min-size="30">
                    <SectionCards
                        v-bind:title="title"
                        v-bind:part="part"
                        v-bind:supList="supList"
                    />
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
import SectionCards from "../components/PDPart/SectionCards.vue";
import {getSupplementalContentNew} from "../utilities/api"
import "splitpanes/dist/splitpanes.css";
import ResourceFilters from "../components/ResourcesPage/ResourceFilters.vue";
export default {
    name: "ResourcePage",
    components: {
        FlashBanner,
        Header,
        Footer,
        Splitpanes,
        Pane,
        ResourceFilters,
        SectionCards,
    },
    data: () => ({
        supList: [],
        title: "kdfjdk",
        part: "323",
        filters: [],
        singleSupList:[]
    }),
    methods: {
        setResourcesParams(payload) {
            console.log("hit");
            this.filters = payload;
            for(let part in this.filters){
                console.log(this.filters[part])
            }
            this.getSupContent();
            // Implement response to user choosing a section or subpart here
        },
        async getSupContent() {
            try {
                this.supList=[]
                for (let part in this.filters) {
                    let query= this.filters[part]
                    console.log(query)
                    this.supList.push(
                        await getSupplementalContentNew(
                            42,
                            query['part'],
                            query['sections'],
                            query['subparts']
                        )
                    );
                }
                for(let sup of this.supList){
                    this.singleSupList.push(sup)
                }
                this.singleSupList = 
                console.log(this.supList);
            } catch (error) {
                console.error(error);
            } finally {
                console.log(this.structure);
            }
        },
    },
};
</script>
<style>
</style>

