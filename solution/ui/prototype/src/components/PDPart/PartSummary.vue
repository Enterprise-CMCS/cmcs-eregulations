<template>
    <div>
        <h3>Part Summary</h3>
        <p>Summary of the part</p>
        <ExpansionMenu
            v-bind:header="'Featured Topics'"
            v-bind:subpiece="'Topic'"
            v-bind:content="'content'"
            v-bind="'true'"
        />

        <h3 style="display: inline">
            Part {{ part }} Federal Register Documents
        </h3>
        <template v-if="!panel.length">
            <v-btn style="float: right" @click="all" text
                >Expand All</v-btn
            ></template
        >
        <template v-else>
            <v-btn style="float: right" @click="hide" text
                >Hide All</v-btn
            ></template
        >
        <v-expansion-panels v-model="panel" multiple accordion>
            <v-expansion-panel>
                <v-expansion-panel-content>
                    <RelatedRules v-bind:title="title" v-bind:part="part"
                /></v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>

        <ExpansionMenu
            v-bind:header="'Miscellaneous Resources not Tied to a Regulation'"
            v-bind:subpiece="'Misc.'"
            v-bind:content="'content'"
            v-bind="'true'"
        />
        <br />
        <v-btn color="#046791" class="white--text">View All Resources</v-btn>
    </div>
</template>
<script>
import ExpansionMenu from "./ExpansionMenu.vue";
import RelatedRules from "../../../../regulations/js/src/components/RelatedRules.vue";
export default {
    name: "PartSummary",
    components: {
        ExpansionMenu,
        RelatedRules,
    },
    data: () => ({
        show: false,
        documentHeader: "Part {{ part }} Federal Register Documents",
        panel: [],
        items: 3,
    }),
    props: {
        title: { type: Number },
        part: { type: Number },
    },
    data() {
        return {
            panel: [],
            items: 3,
        };
    },
    methods: {
        all() {
            this.panel = [...Array(this.items).keys()].map((k, i) => i);
        },

        hide() {
            this.panel = [];
        },
    },
};
</script>

<style>
.v-expansion-panel-header {
    color: #046791;
    padding: 0px 0px;
    box-shadow: none;
}
.v-expansion-panel::before {
    box-shadow: none;
}
.v-expansion-panel:not(:first-child)::after {
    border: none;
}
</style>