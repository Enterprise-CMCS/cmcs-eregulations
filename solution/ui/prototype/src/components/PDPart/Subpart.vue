<template>
    <div>
        <h3>Subpart Resources</h3>
        <p>Subpart Description</p>

        <ExpansionMenu
            v-bind:header="'Subparts'"
            v-bind:data="subparts"
            v-bind:content="'content'"
            v-bind="'true'"
        />
            <supplemental-content-category
                v-for="category in supList"
                :key="category.name"
                :name="category.name"
                :description="category.description" 
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
                :isFetching=true
            >
            </supplemental-content-category>
        <br />
        <v-btn color="#046791" class="white--text">View All Resources</v-btn>
    </div>
</template>
<script>

import ExpansionMenu from './ExpansionMenu.vue'
import { getSupplementalContentNew } from "@/utilities/api";
import SupplementalContentCategory from "../../../../regulations/js/src/components/SupplementalContentCategory.vue"
export default({
    name:"SubpartResources",
    props: {
        title: { type: Number },
        part: { type: Number },   
        subparts: {type: Array, required:false},
        supList: []
    },
    components: {
        ExpansionMenu,
        getSupplementalContentNew,
        SupplementalContentCategory
    },


    async created() {
        try {
            console.log([this.subparts[0].label[0]])
            this.supList = await getSupplementalContentNew(
                '42',
                '435',
                [],
                [this.subparts[0].label[0]]
            );
        } catch (error) {
            console.error(error);
        } finally {
            console.log(this.structure);
        }
    },

})
</script>
