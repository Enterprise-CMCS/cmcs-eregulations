<template v-slot:extension>
    <div>
        <v-tabs v-model="tab">
            <v-tab v-for="tab in tabs" :key="tab">{{ tab }}</v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
            <v-tab-item v-for="d in tabs" :key="d">
                <template v-if="tabs[tab] === 'Section'">
                    <v-container fluid
                        ><v-row dense v-for="i in d"
                            ><SectionCards class="section-cards" v-bind:title="title" v-bind:part="part" /> </v-row
                    ></v-container>
                </template>
                <template v-else-if="tabs[tab] === 'Part'"
                    ><PartSummary v-bind:title="title" v-bind:part="part"
                /></template>
                <template v-else-if="tabs[tab]=== 'Subpart'">
                    <SubpartResources v-bind:subparts="subparts" /></template>
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
        SubpartResources
    },
    name: "RightColumn",
    props: {
        title: { type: Number },
        part: { type: Number },   
        subparts: {type: Array, required:false}
     
    },
    data() {
        return {
            tab: null,
            tabs: ["Part", "Subpart", "Section"],
        };
    },
    computed:{
        subpartList: function (){
            
        }
    }
};
</script>
<style scoped>
.section-cards {
    margin-bottom: 10px;
}
</style>
