<template>
    <div>
        <div>
            <h3 style="display: inline">{{ header }}</h3>
            <template v-if="!panel.length">
            <v-btn  style="float: right" @click="all" text>Expand All</v-btn></template>
            <template v-else>
            <v-btn style="float: right" @click="hide" text>Hide All</v-btn></template>
        </div>
        <v-expansion-panels v-model="panel" multiple accordion>
            <v-expansion-panel v-for="(item, i) in 3" :key="i">
                <v-expansion-panel-header>
                    {{ subpiece }}
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    {{ content }}
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
    </div>
</template>

<script>
export default {
    name: "ExpansionMenu",
    props: {
        header: { type: String },
        subpiece: { type: Number },
        content: { type: String },
        expandAll: { type: Boolean },
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

        hide(){
            this.panel= []
        }
    },
};
</script>
