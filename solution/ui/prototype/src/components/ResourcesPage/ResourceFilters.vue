<template>
    <div class="resourcefilters">
        <h2>Filters</h2>
        <h3>Resource Type</h3>


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
import { getSupplementalContentNew, getCategories } from "@/utilities/api";

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
        categories: [],
        categoryDict: {},
                value: null,
        // define options
        options: [ {
          id: 'a',
          label: 'a',
          children: [ {
            id: 'aa',
            label: 'aa',
          }, {
            id: 'ab',
            label: 'ab',
          } ],
        }, {
          id: 'b',
          label: 'b',
        }, {
          id: 'c',
          label: 'c',
        } ],
    }),
    components:{Treeselect},
    methods: {
        organizeCategories: function (categories) {
            console.log(categories);

            for (let category in categories) {
                let cat = categories[category];
                console.log(cat.object_type);
                if (cat.object_type === "subcategory") {
                    if (cat.parent.name in this.categoryDict) {
                        this.categoryDict[cat.parent.name].subcategories.push(
                            cat.name
                        );
                    } else {
                        this.categoryDict[cat.parent.name] = {
                            subcategories: [cat.name],
                        };
                    }
                } else if (!(cat.name in this.categoryDict)) {
                    this.categoryDict[cat.name] = { subcategories: [] };
                }
            }
            this.categories= [this.categoryDict]
            //console.log(this.categoryDict)
        },
    },
    async created() {
        try {
            this.supList = await getSupplementalContentNew(42, 441, [], ["B"]);
            this.categories = await getCategories();
            this.categories = this.organizeCategories(this.categories);
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
