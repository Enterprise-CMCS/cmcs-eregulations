<template>
    <div style="width: 100%; margin: 20px">
        <div>
            <h2 style="display: inline">
                <Breadcrumbs
                    :title="title"
                    :part="part"
                    :subPart="subPart"
                    :section="section"
                />
            </h2>
            <span style="float: right" class="breadcrumbs">
                <router-link
                    v-if="navigation.previous"
                    :to="{
                        name: navigation.name,
                        params: navigation.previous,
                    }"
                    >Previous</router-link
                >
                <span v-else>Previous</span>
                /
                <router-link
                    v-if="navigation.next"
                    :to="{
                        name: navigation.name,
                        params: navigation.next,
                    }"
                    >Next</router-link
                >
                <span v-else>Next</span>
            </span>
        </div>

        <v-expansion-panels>
            <v-expansion-panel>
                <v-expansion-panel-header>
                    <span class="v-expansion-panel-header-text">Table of Contents</span>
                    <template v-slot:actions>
                        <v-icon color="black">
                            mdi-plus
                        </v-icon>
                    </template>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <PartToc :structure="tocContent" navName="PDpart" />
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
        <h1 style="margin-bottom:0px" v-if="!subPart && !section">Part {{this.part}} - {{ this.partLabel }}</h1>
        <PartContent
            v-if="structure.length"
            :structure="structure"
            :title="title"
            :part="part"
            resourcesDisplay="drawer"
            :showResourceButtons="false"
            :supplementalContentCount="supplementalContentCount"
            @view-resources="setResourcesParams"
        />
        <div v-else>Regulation not found</div>
    </div>
</template>

<script>
import PartContent from "@/components/part/PartContent.vue";
import Breadcrumbs from "@/components/PDPart/Breadcrumbs.vue";
import PartToc from "@/components/part/PartToc";

export default {
    name: "LeftColumn",
    components: {
      PartToc,
        PartContent,
        Breadcrumbs,
    },
    props: {
        title: { type: String },
        part: { type: String },
        subPart: { type: String },
        section: { type: String },
        structure: { type: Array },
        tocContent: {type: Object},
        navigation: { type: Object },
        supplementalContentCount: { type: Object },
        partLabel: {type: String},
    },
    methods: {
        setResourcesParams(payload) {
            let scope = payload["scope"];
            let identifier = payload["identifier"];

            this.$emit("view-resources", {
                scope,
                identifier,
            });
        },
    },
};
</script>

<style scoped>
  .breadcrumbs{
      font-family: Open Sans;
      font-size: 12px;
      font-style: normal;
      font-weight: 700;
      line-height: 30px;
      letter-spacing: 0em;
      text-align: left;
  }
  .toc-group{
    margin-top: 5px;
  }
  .toc{
    margin-left:0;
  }
  .v-expansion-panel{
    border: 3px solid #f3f3f3;
  }

  .v-expansion-panel-header{
    background-color: #f3f3f3;
    color: black;
    font-weight: bold;
    font-size: 16px;
    line-height: 20px
  }
  .v-expansion-panel-header-text{
    padding:18px;
  }
</style>