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
                        <v-select
                            :items="[1,2,3,4,5]"
                            multiple
                            outlined
                            chips
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
                            chips
                        />
                    </v-col>
                </v-row>
            </v-container>
        </div>
        <TabFilters
            :title="title"
            :part="part"
            :sup-list="supList"
            :suggestedTab="suggestedTab"
        />
    </div>
</template>

<script>
import TabFilters from "./TabFilters.vue";
export default {
    name: "RightColumn",
    components: {
        TabFilters,
    },
    props: {
        title: { type: String },
        part: { type: String },
        supList: { type: Array },
        suggestedTab: { type: String},
    },
    data() {
        return {
            tabs: null,
            showFilter:false
        };
    },
    watch: {
      supList:{
          async handler() {
            this.tabs = 2
          }
      }
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