<template v-slot:extension>
    <div>
        <div class="tab-bar">
            <v-tabs v-model="tab">
                <v-tab v-for="tab in tabTitles" :key="tab">{{ tab }} </v-tab>
            </v-tabs>
        </div>
        <v-tabs-items v-model="tab">
            <v-tab-item>
                <PartSummary v-bind:title="title" v-bind:part="part"/>
            </v-tab-item>
            <v-tab-item>
                <SubpartResources v-bind:title="title" v-bind:part="part" :suggestedSubPart="suggestedSubPart" />
            </v-tab-item>
            <v-tab-item>
                <v-container fluid>
                    <SectionCards
                        v-bind:title="title"
                        v-bind:part="part"
                        v-bind:supList="supList"
                    />
                </v-container>
            </v-tab-item>
        </v-tabs-items>
    </div>
</template>
<script>
import TabFilters from "./TabFilters.vue";
import SectionCards from "./SectionCards.vue";
import PartSummary from "./PartSummary.vue";
import SubpartResources from "./Subpart.vue";
import {capitalizeFirstLetter} from "../../utilities/utils";
export default {
    components: {
        TabFilters,
        SectionCards,
        PartSummary,
        SubpartResources,
    },
    name: "RightColumn",
    props: {
        title: { type: String },
        part: { type: String },
        supList: { type: Array },
        suggestedTab: {type: String },
        suggestedSubPart: { type: String},
    },
    data() {
        return {
            tab: null,
            tabs: ["Part", "Subpart", "Section"],
        };
    },
    computed: {
        subpartList: function () {},
        tabTitles: function(){
            const tabList = ["Part", "Subpart"]
            let count = 0
            this.supList.forEach( category => {
              count += category.supplemental_content.length
              category.sub_categories.forEach( subCategory => {
                count += subCategory.supplemental_content.length
              })
            })
            tabList.push(this.supList.length ? `Section (${count})` : "section")
            return tabList
        }
    },
    watch: {
      suggestedTab:{
          async handler(suggestedTab) {
            this.tab = this.tabs.indexOf(capitalizeFirstLetter(suggestedTab)) || 5
          }
      }
    }
};
</script>

<style scoped>
.tab-bar {
    border-bottom: 1px solid #d6d7d9;
}
</style>
