<template>
    <div style="width:100%; margin:20px">
        <div>
            <h2 style="display: inline">
                <Breadcrumbs
                    :title="title"
                    :part="part"
                    :subPart="subPart"
                    :section="section"
                />
            </h2>
            <span style="float:right">
                <router-link
                    v-if="navigation.previous"
                    :to="{
                        name: navigation.name,
                        params: navigation.previous,
                    }"

                >Previous</router-link>
                <span v-else>Previous</span>
                /
                <router-link
                    v-if="navigation.next"
                    :to="{
                        name: navigation.name,
                        params: navigation.next,
                    }"
                >Next</router-link>
                <span v-else>Next</span>
            </span>
        </div>

        <v-expansion-panels>
            <v-expansion-panel>
                <v-expansion-panel-header>
                    Table of Contents
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    TABLE OF CONTENTS HERE
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>

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

export default {
  name: "LeftColumn",
  components: {
        PartContent,
        Breadcrumbs
    },
  props:{
    title: {type:String},
    part: {type: String},
    subPart: {type: String},
    section: {type: String},
    structure: {type: Array},
    navigation: {type: Object},
    supplementalContentCount: {type:Object},

  },
  methods: {
    setResourcesParams(payload) {
        console.log(payload)
    },
  },

}
</script>

<style scoped>

</style>