<template>
    <div class="section-display">
    <div class="flex-parent-element">
    <div class="flex-child-element">
            <h2 v-bind:class="{ 'search-header': usingSearch }">{{supList.length}} Results</h2>
            <p class="search-subtitle" v-if="usingSearch">For "{{searchQuery}}".</p>
            </div>
         
            <div> <v-select v-model="sortBy" label="Sort By" :items='sortList'></v-select>
            </div></div>
            <div class="section-cards">
            <div class="section-cards" v-for="content in supList" :key="content.name">
        <SectionCard v-bind:f="content" v-bind:usingSearch="usingSearch" /></div></div>

    </div>
    
</template>
<script>

import SectionCard from "../PDPart/SectionCard.vue"

export default {
    name: "SectionPane",
    props: ["supList", "usingSearch", "searchQuery"],
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
.search-header {
  margin-bottom: 0;
  padding-bottom: 0;
}
.search-subtitle {
  margin-top: 0;
  padding-top: 0;
}
</style>
