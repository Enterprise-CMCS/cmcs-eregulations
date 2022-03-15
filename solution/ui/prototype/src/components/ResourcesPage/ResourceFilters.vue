<template>
    <div class="resourcefilters">
        <h2>Filters</h2>
        <h3>Resource Type</h3>

        <v-select
            multiple
            v-model="selectedResources"
            :items="resources"
            outlined
        ></v-select>
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
import { getSupplementalContentNew } from "@/utilities/api";
export default {
    name: "ResourceFilters",
    data: () => ({
        titles: ["42"],
        parts: ["foo", "bar", "fizz"],
        sections: ["sections"],
        resources: ["resources"],
        selectedResources: [],
        selectedParts: [],
        selectedSections: [],
        selectedTitles: [],
        supList: [],
    }),

    async created() {
        try {
            this.supList = await getSupplementalContentNew(42, 441, [], ["B"]);
        } catch (error) {
            console.error(error);
        } finally {
            console.log(this.supList);
        }
    },
};
</script>

<style scoped>
.resourcefilters {
    padding: 20px;
}
</style>
