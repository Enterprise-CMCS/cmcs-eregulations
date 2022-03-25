<template>
    <div>
        <h3>Subpart Resources</h3>
        <p>Subpart Description</p>

        <h3 style="display: inline">
            Subparts
        </h3>
        <template v-if="this.panel.length <= 0">
            <v-btn
                style="float: right"
                text
                @click="all"
            >
                Expand All
            </v-btn>
        </template>
        <template v-else>
            <v-btn
                style="float: right"
                text
                @click="hide"
            >
                Hide All
            </v-btn>
        </template>
        <v-expansion-panels
            v-model="panel"
            accordion
            multiple
        >
            <v-expansion-panel
                v-for="(subpart, i) in subParts"
                :key="i"
            >
                <v-expansion-panel-header>
                    {{ subpart.label }}
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <SubpartSupplement
                        :title="title"
                        :part="part"
                        :subpart="subpart.identifier"
                    />
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
        <br />
    </div>
</template>
<script>
import { getSupplementalContentNew, getSubPartsForPart } from "@/utilities/api";
import SupplementalContentCategory from "legacy/js/src/components/SupplementalContentCategory.vue";
import SubpartSupplement from "./SubpartSupplemental.vue";

// This is not ideal, but sb fine for now.
const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


export default {
    name: "SubpartResources",
    components: {
        getSupplementalContentNew,
        SupplementalContentCategory,
        SubpartSupplement,
    },
    props: {
        title: { type: String },
        part: { type: String },
        suggestedSubPart: {type: String},

    },
    data() {
        return {
            panel: [],
            subParts: null,

        };
    },
    watch:{
      suggestedSubPart: {
          async handler(newSuggestion) {
            this.panel.push(alphabet.indexOf(newSuggestion))
          }
      }
    },
    async created() {
        try {
            this.subParts = await getSubPartsForPart(this.part);
        } catch (error) {
            console.error(error);
        } finally {
          if(this.suggestedSubPart) {
            this.panel.push(alphabet.indexOf(this.suggestedSubPart))
          }
            console.log(this.subParts);
        }
    },
    methods: {
        all() {
            this.panel = [...Array(this.subParts.length).keys()];
        },

        hide() {
            this.panel = [];
        },
    },
};
</script>
