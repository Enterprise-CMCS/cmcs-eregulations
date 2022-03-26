<template>
    <div style="width: 100%; margin: 20px">
        <div>
            <h2 style="display: inline">
                Part {{ part }} resources
            </h2>
            <span style="float: right">
                <a @click="showFilter = !showFilter">Filter and sort resources</a>
            </span>
        </div>
        <div>
            <v-text-field
                clearable
                outlined
                class="example"
            />
        </div>
        <div v-if="showFilter">
            <v-container fluid>
                <v-row
                    align="center"
                >
                    <v-col
                        cols="8"
                    >
                        <label
                            class="label"
                            style="display: inline"
                        >Resource Type</label>
                        <treeselect
                            v-model="selectedResources"
                            :multiple="true"
                            value-consists-of="ALL_WITH_INDETERMINATE"
                            :options="this.catOptions"

                        />
                    </v-col>
                    <v-col
                        cols="3"
                    >
                        <label
                            class="label"
                            style="display: inline"
                        >Sort by</label>
                        <v-select
                            :items="['Relevance', 'Most Recent', 'Regulation hierarchy', 'Resource type']"
                            outlined
                            dense
                        />
                    </v-col>
                </v-row>
            </v-container>
        </div>
        <TabFilters
            :title="title"
            :part="part"
            :sub-part="subPart"
            :section="section"
            :sup-list="supList"
            :suggested-tab="suggestedTab"
            :suggested-sub-part="suggestedSubPart"
        />
    </div>
</template>

<script>
import TabFilters from "./TabFilters.vue";
import { getCategories } from "@/utilities/api";
import { getCategoryTree } from "@/utilities/utils";
import Treeselect from "@riophae/vue-treeselect";
import "@riophae/vue-treeselect/dist/vue-treeselect.css";

export default {
    name: "RightColumn",
    components: {
        TabFilters,
        Treeselect,
    },
    props: {
        title: { type: String },
        part: { type: String },
        supList: { type: Array },
        suggestedTab: { type: String},
        suggestedSubPart: { type: String},
        subPart: { type: String },
        section: { type: String },
    },
    data() {
        return {
            tabs: null,
            showFilter:false,
            selectedResources: [],
            categories: [],
            catOptions: [],

        };
    },
    watch: {
      supList:{
          async handler() {
            this.tabs = 2
          }
      }
    },
    async created(){
      this.categories = await getCategories();
      this.catOptions = getCategoryTree(this.categories);
    }
};
</script>

<style>
.v-text-field.v-text-field--enclosed .v-input__slot {
    width: 90% !important;
    max-width: 90% !important;
}
.label{
  font-size: 14px;
  font-weight: 700;
}
</style>