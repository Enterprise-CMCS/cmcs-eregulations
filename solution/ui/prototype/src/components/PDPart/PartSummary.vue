<template>
    <div>
        <h3>Part Summary</h3>
        <p>Summary of the part</p>

        <div>
            <h3 style="display: inline">Featured Topics</h3>
            <template v-if="!topicPanel.length">
                <v-btn style="float: right" @click="show_topics" text
                    >Expand All</v-btn
                ></template
            >
            <template v-else>
                <v-btn style="float: right" @click="hide_topics" text
                    >Hide All</v-btn
                ></template
            >
            <v-expansion-panels v-model="topicPanel" multiple accordion>
                <v-expansion-panel>
                    <v-expansion-panel-content v-for="i in 3" :key="i">
                        Featured topic {{ i }}</v-expansion-panel-content
                    >
                </v-expansion-panel>
            </v-expansion-panels>
        </div>
        <h3 style="display: inline">
            Part {{ part }} Federal Register Documents
        </h3>
        <template v-if="!documentPanel.length">
            <v-btn style="float: right" @click="show_documents" text
                >Expand All</v-btn
            ></template
        >
        <template v-else>
            <v-btn style="float: right" @click="hide_documents" text
                >Hide All</v-btn
            ></template
        >

        <v-expansion-panels v-model="documentPanel" multiple accordion>
            <v-expansion-panel>
                <v-expansion-panel-content>
                    <RelatedRules v-bind:title="title" v-bind:part="part"
                /></v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>

        <div>
            <h3 style="display: inline">
                Miscellaneous Resources not Tied to a Regulation
            </h3>
            <template v-if="!miscPanel.length">
                <v-btn style="float: right" @click="show_misc" text
                    >Expand All</v-btn
                ></template
            >
            <template v-else>
                <v-btn style="float: right" @click="hide_misc" text
                    >Hide All</v-btn
                ></template
            >
            <v-expansion-panels v-model="miscPanel" multiple accordion>
                <v-expansion-panel>
                    <v-expansion-panel-content v-for="i in 3" :key="i">
                        Misc {{ i }}</v-expansion-panel-content
                    >
                </v-expansion-panel>
            </v-expansion-panels>
        </div>
        <br />
        <router-link :to="{
            name:'PDResources',
            query: { part, title, subPart, section }
        }">
            <v-btn color="#046791" class="white--text">View All Resources</v-btn>
        </router-link>
    </div>
</template>
<script>
import RelatedRules from "legacy/js/src/components/RelatedRules.vue";
export default {
    name: "PartSummary",
    components: {
        RelatedRules,
    },
    data: () => ({
        show: false,
        documentHeader: "Part {{ part }} Federal Register Documents",
        topicPanel: [],
        documentPanel:[],
        miscPanel:[],
    }),
    props: {
        title: { type: String },
        part: { type: String },
        subPart: { type: String },
        section: { type: String },
    },

    methods: {
        
        show_topics() {
            this.topicPanel = [...Array(this.topicPanel).keys()];
        },

        hide_topics() {
            this.topicPanel = [];
        },
        show_documents() {
            this.documentPanel = [...Array(this.documentPanel).keys()];
        },

        hide_documents() {
            this.documentPanel = [];
        },
        show_misc() {
            this.miscPanel = [...Array(this.miscPanel).keys()];
        },

        hide_misc() {
            this.miscPanel = [];
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