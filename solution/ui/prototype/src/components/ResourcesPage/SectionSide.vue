<template>
    <div class="section-display">
    <div class="flex-parent-element">
    <div class="flex-child-element">
            <h2>{{supList.length}} Results</h2></div>
         
            <div> <v-select v-model="sortBy" label="Sort By" :items='sortList'></v-select>
            </div></div>
            <div class="section-cards">
            <div class="section-cards" v-for="content in supList" :key="content.name">
        <SectionCard v-bind:f="content" /></div></div>

    </div>
    
</template>
<script>

import SectionCard from "../PDPart/SectionCard.vue"

export default {
    name: "SectionPane",
    props: ["supList"],
    data: () =>({
        sortList:['Relevance', 'Most recent', 'Regulation hieracry', 'Resource type'],
        sortBy: 'Relevance'
    }),
    components: {
        SectionCard,
    },
};
</script>
<style scoped>
.section-display {
    padding: 30px;
    width:100%;
}
.section-cards{
padding-bottom: 10px;
padding-top:10px;
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
