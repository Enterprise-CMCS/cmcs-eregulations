<template>
    <div style="width: 100%; margin: 20px">
        <div>
            <h2 style="display: inline">
                <Breadcrumbs :title="title" :part="part" :subPart="subPart" :section="section" />
            </h2>
            <span style="float: right" class="breadcrumbs" v-if="subPart != 'Subpart-undefined'">
                <router-link v-if="navigation.previous" :to="{
                    name: navigation.name,
                    params: navigation.previous,
                }">Previous</router-link>
                <span v-if="navigation.previous && navigation.next"> | </span>
                <router-link v-if="navigation.next" :to="{
                    name: navigation.name,
                    params: navigation.next,
                }">Next</router-link>
            </span>
        </div>

        <v-expansion-panels v-model="panel">
            <v-expansion-panel>
                <v-expansion-panel-header disable-icon-rotate>
                    <span class="v-expansion-panel-header-text">Table of Contents</span>
                    <template v-slot:actions>
                        <v-icon color="black">
                            mdi-plus
                        </v-icon>
                    </template>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <PartToc :structure="tocContent" navName="PDpart" @exitTOC="closeTOC" />
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
        <h1 style="margin-bottom:0px" v-if="!subPart && !section">Part {{ this.part }} - {{ this.partLabel }}</h1>
        <PartContent v-if="structure.length" :structure="structure" :title="title" :part="part" :subpart="subPart"
            resourcesDisplay="drawer" :showResourceButtons="true" :supplementalContentCount="supplementalContentCount" :headerLinks="true"
            @view-resources="setResourcesParams" />
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
        subPart: { type: String, required: false, default: "" },
        section: { type: String },
        structure: { type: Array },
        tocContent: {type: Object},
        navigation: { type: Object },
        supplementalContentCount: { type: Object },
        partLabel: { type: String },
    },
    data(){
        return{
            panel:[]
        }
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
        closeTOC(){
            this.panel=[]
        }
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
  .v-expansion-panel button {
    padding: 0;
  }

  .v-expansion-panel-header{
    background-color: #f3f3f3;
    color: black;
    font-weight: bold;
    font-size: 16px;
    line-height: 20px
  }

  .v-expansion-panel-header__icon.v-expansion-panel-header__icon--disable-rotate i {
    width: 40px;
  }

  .v-expansion-panel-header-text{
    padding:18px;
  }
</style>