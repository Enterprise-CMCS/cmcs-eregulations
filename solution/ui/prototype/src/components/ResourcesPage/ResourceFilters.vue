<template>
    <div class="resourcefilters">
        <h2>Filters</h2>
        <h3>Resource Type</h3>
        <treeselect
            v-model="this.resourcesValues"
            :multiple="true"
            :options="this.catOptions"
        />

        <h3>Title</h3>

        <v-autocomplete
            multiple
            v-model="selectedTitles"
            :items="titles"
            chips
            outlined
        ></v-autocomplete>
        <h3>Part</h3>
        <v-autocomplete
            multiple
            chips
            v-model="selectedParts"
            :items="parts"
            v-on:change="filterSections"
            item-value="id"
            item-text="name"
            outlined
        ></v-autocomplete>
        <h3>Section</h3>

        <v-autocomplete
            multiple
            v-model="selectedSections"
            :items="this.filteredSections"
            item-value="location"
            item-text="label"
            chips
            outlined
            v-on:change="get_filter"
        ></v-autocomplete>
    </div>
</template>
<script>
import {
    getCategories,
    getPartsDetails,
    getSubPartsandSections,
} from "@/utilities/api";
import { getCategoryTree } from "@/utilities/utils";
import Treeselect from "@riophae/vue-treeselect";

import "@riophae/vue-treeselect/dist/vue-treeselect.css";

export default {
    name: "ResourceFilters",
    components: { Treeselect },
    props: {
        resourceParamsEmitter: {
            type: Function,
            required: false,
        },
    },
    data: () => ({
        titles: ["42"],
        parts: [],
        sections: ["sections"],
        resourcesValues: [],
        selectedResources: [],
        selectedParts: [],
        selectedSections: [],
        selectedTitles: [],
        categories: [],
        catOptions: [],
        filteredSections:[],
        filters:{}
    }),

    methods: {
        filterSections(parts) {
            if (parts.length > 0) {
                this.filteredSections = this.sections.filter((section) =>
                    parts.includes(section.location.part)
                );
            } else {
                this.filteredSections = this.sections;
            }
            this.get_filter();
        },
        get_filter(){
            this.filters={}
           
            for(let part of this.selectedParts){
                this.filters[part]={part:part, subparts:[], sections:[]}
            }
            
            for(let section of this.selectedSections){
                if(!this.filters[section.part]){
                    this.filters[section.part]={part:section.part, subparts:[], sections:[]}
                }
                if(section.section){
                    this.filters[section.part].sections.push(section.section)
                }
                else{
                    this.filters[section.part].subparts.push(section.subpart)
                }
            }
            console.log(this.filters)
            this.resourceParamsEmitter(this.filters)
        },
    },
    async created() {
        try {
            this.parts = await getPartsDetails();
            this.categories = await getCategories();
            this.catOptions = getCategoryTree(this.categories);
            this.sections = await getSubPartsandSections();
            this.filteredSections = this.sections;
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
