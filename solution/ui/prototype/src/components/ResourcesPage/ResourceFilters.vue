<template>
    <div class="resourcefilters">
        <h2>Filters</h2>
        <h3>Resource Type</h3>
     <treeselect v-model="value" :multiple="true" :options="this.catOptions" />

        <h3>Title</h3>
  
        <v-select
            multiple
            v-model="selectedTitles"
            :items="titles"
            outlined
        ></v-select>
        <h3>Part</h3>
        <v-select
            multiple
            v-model="selectedParts"
            :items="parts"
            outlined
        ></v-select>
        <h3>Section</h3>
        <v-select
            multiple
            v-model="selectedSections"
            :items="sections"
            outlined
        ></v-select>
    </div>
</template>
<script>

import { getSupplementalContentNew, getCategories, getAllParts } from "@/utilities/api";
import { getCategoryTree } from "@/utilities/utils";
import Treeselect from '@riophae/vue-treeselect'

import '@riophae/vue-treeselect/dist/vue-treeselect.css'

export default {
    name: "ResourceFilters",
    components: { Treeselect },
    data: () => ({
        titles: ["42"],
        parts: [],
        sections: ["sections"],
        resources: ["resources"],
        selectedResources: [],
        selectedParts: [],
        selectedSections: [],
        selectedTitles: [],
        supList: [],
        categories: [],
        catOptions:[],
        value: null,

    }),
 
    async created() {
        try {
            this.supList = await getSupplementalContentNew(42, 441, [], ["B"]);
            this.parts = await getAllParts();
            this.categories = await getCategories();
            this.catOptions = getCategoryTree(this.categories);
        } catch (error) {
            console.error(error);
        } finally {
        }
    },
};
</script>

<style scoped>
.resourcefilters {
    padding: 20px;
}
</style>
