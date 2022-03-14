<template v-slot:extension>
    <div>
        <div class="tab-bar">
            <v-tabs v-model="tab">
                <v-tab v-for="tab in tabs" :key="tab">{{ tab }}</v-tab>
            </v-tabs>
        </div>
        <v-tabs-items v-model="tab">
            <v-tab-item
                ><PartSummary v-bind:title="title" v-bind:part="part"
            /></v-tab-item>
            <v-tab-item>
                <SubpartResources v-bind:title="title" v-bind:part="part" />
            </v-tab-item>
            <v-tab-item>
                <v-container fluid
                    ><SectionCards
                        v-bind:title="title"
                        v-bind:part="part"
                        v-bind:selectedSection="selectedSection"
                /></v-container>
            </v-tab-item>
        </v-tabs-items>
    </div>
</template>
<script>
import TabFilters from "./TabFilters.vue";
import SectionCards from "./SectionCards.vue";
import PartSummary from "./PartSummary.vue";
import SubpartResources from "./Subpart.vue";
export default {
    components: {
        TabFilters,
        SectionCards,
        PartSummary,
        SubpartResources,
    },
    name: "RightColumn",
    props: {
        title: { type: String },
        part: { type: String },
        selectedSection: { type: String },
    },
    data() {
        return {
            tab: null,
            tabs: ["Part", "Subpart", "Section"],
        };
    },
    computed: {
        subpartList: function () {},
    },
};
</script>

<style scoped>
.tab-bar {
    border-bottom: 1px solid #d6d7d9;
}
</style>
