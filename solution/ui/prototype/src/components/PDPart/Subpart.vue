<template>
    <div>
        <h3>Subpart Resources</h3>
        <p>Subpart Description</p>

        <h3 style="display: inline">Subparts</h3>
        <template v-if="panel.length">
            <v-btn style="float: right" @click="all" text
                >Expand All</v-btn
            ></template
        >
        <template v-else>
            <v-btn style="float: right" @click="hide" text
                >Hide All</v-btn
            ></template
        >
        <v-expansion-panels accordion>
            <v-expansion-panel v-for="(subpart, i) in subParts" :key="i">
                <v-expansion-panel-header
                    >Subpart {{ subpart }}</v-expansion-panel-header
                >
                <v-expansion-panel-content
                    ><SubpartSupplement
                        v-bind:title="title"
                        v-bind:part="part"
                        v-bind:subpart="subpart" /></v-expansion-panel-content
            ></v-expansion-panel>
        </v-expansion-panels>

        <supplemental-content-category
            v-for="category in supList"
            :key="category.name"
            :name="category.name"
            :description="category.description"
            :supplemental_content="category.supplemental_content"
            :sub_categories="category.sub_categories"
            :isFetching="true"
        >
        </supplemental-content-category>
        <br />
    </div>
</template>
<script>
import ExpansionMenu from "./ExpansionMenu.vue";
import { getSupplementalContentNew, getSubPartsForPart } from "@/utilities/api";
import SupplementalContentCategory from "../../../../regulations/js/src/components/SupplementalContentCategory.vue";
import SubpartSupplement from "./SubpartSupplemental.vue";
export default {
    name: "SubpartResources",
    props: {
        title: { type: String },
        part: { type: String },
    },
    components: {
        ExpansionMenu,
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
            this.panel = [...Array(this.panel).keys()].map((k, i) => i);
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
            console.log(this.supList);
        }
    },
};
</script>
