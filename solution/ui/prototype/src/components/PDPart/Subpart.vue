<template>
    <div>
        <h3>Subpart Resources</h3>
        <p>Subpart Description</p>

        <h3 style="display: inline">Subparts</h3>
        <template v-if="this.panel.length <= 0">
            <v-btn style="float: right" @click="all" text
                >Expand All</v-btn
            ></template
        >
        <template v-else>
            <v-btn style="float: right" @click="hide" text
                >Hide All</v-btn
            ></template
        >
        <v-expansion-panels accordion multiple v-model="panel">
            <v-expansion-panel v-for="(subpart, i) in subParts" :key="i">
                <v-expansion-panel-header>{{
                    subpart.label
                }}</v-expansion-panel-header>
                <v-expansion-panel-content
                    ><SubpartSupplement
                        v-bind:title="title"
                        v-bind:part="part"
                        v-bind:subpart="
                            subpart.identifier
                        " /></v-expansion-panel-content
            ></v-expansion-panel>
        </v-expansion-panels>
        <br />
    </div>
</template>
<script>
import { getSupplementalContentNew, getSubPartsForPart } from "@/utilities/api";
import SupplementalContentCategory from "legacy/js/src/components/SupplementalContentCategory.vue";
import SubpartSupplement from "./SubpartSupplemental.vue";
export default {
    name: "SubpartResources",
    props: {
        title: { type: String },
        part: { type: String },
    },
    components: {
        getSupplementalContentNew,
        SupplementalContentCategory,
        SubpartSupplement,
    },
    data() {
        return {
            panel: [],
            subParts: null,
        };
    },

    methods: {
        all() {
            this.panel = [...Array(this.subParts.length).keys()];
        },

        hide() {
            this.panel = [];
        },
    },
    async created() {
        try {
            this.subParts = await getSubPartsForPart(this.part);
        } catch (error) {
            console.error(error);
        } finally {
            console.log(this.subParts);
        }
    },
};
</script>
