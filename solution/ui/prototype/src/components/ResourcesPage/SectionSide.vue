<template>
    <div class="section-display">
    <div class="flex-parent-element">
    <div class="flex-child-element">
            <h2>{{supList.length}} Results</h2></div>
         
            <div> <v-select v-model="sortBy" label="Sort By" :items='sortList'></v-select>
            </div></div>
            <div class="section-cards">
            <div v-for="content in supList" :key="content.name">
        <SupplementalCards v-bind:content="content" /></div></div>

    </div>
    
</template>
<script>
import SupplementalCards from "./SupplementalCards.vue"
export default {
    name: "SectionPane",
    props: ["supList"],
    data: () =>({
        sortList:['Relevance', 'Most recent', 'Regulation hieracry', 'Resource type'],
        sortBy: 'Relevance'
    }),
    components: {
        SupplementalCards,
    },
};
</script>
<style scoped>
.section-display {
    padding: 30px;
    width:100%;
}
.section-cards{
padding:30px;
}

.flex-parent-element {
  display: flex;
  width: 100%;
}

.flex-child-element {
  flex: 1;
}
.flex-child-element:last-child {
  flex: 1;
  margin-right: 10px;
}
.flex-child-element:first-child {
  margin-left: 20px;
}
</style>
