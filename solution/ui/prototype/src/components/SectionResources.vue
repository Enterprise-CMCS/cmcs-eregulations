<template>
    <v-dialog
        v-model="dialog"
        fullscreen
        hide-overlay
        transition="dialog-bottom-transition"
    >
        <template v-slot:activator="{ on, attrs }">
            <v-btn
                color="primary"
                dark
                v-bind="attrs"
                v-on="on"
            >
                View Section Resources
            </v-btn>
        </template>
        <v-card style="background-color: #f3f3f3">
            <div class="centered-container" style="margin-bottom: 25px">
                <b style="font-size:30px">§{{ part }}.{{ section }} Resources </b>
                <a style="font-size:14px; margin-left:15px"> Show All Resources</a>
                <v-btn
                    icon
                    class="close-button"
                    @click="dialog = false"
                >
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </div>
            <div class="wrapper centered-container">
                <div class="one">
                    <v-text-field
                        outlined
                        placeholder="Search Resources"
                        append-icon="mdi-magnify"
                    />
                </div>
                <div style="grid-column: 3; text-align:right">
                    <label>Filter By:</label>
                </div>
                <div style="grid-column: 4 / 6;">
                    <v-select
                        outlined
                        :items="availableCategories"
                        v-model="selectedCategory"
                        multiple
                    />
                </div>
            </div>
            <v-divider />

            <div
                v-for="category in availableContent"
                :key="category.name"
                class="centered-container"
            >
                <div class="supplemental-content-category-title">
                    {{ category.name }}
                </div>
                <div class="flex-row-container">
                    <SupplementalContentCard
                        v-for="c in category.supplemental_content"
                        :key="c.url"
                        :supplemental-content="c"
                    />
                </div>
                <div
                    v-for="subcategory in category.sub_categories"
                    :key="subcategory.name"
                >
                    <div class="supplemental-content-subcategory-title">
                        {{ subcategory.name }}
                    </div>
                    <div class="flex-row-container">
                        <SupplementalContentCard
                            v-for="c in subcategory.supplemental_content"
                            :key="c.url"
                            :supplemental-content="c"
                        />
                    </div>
                </div>
                <v-divider />
            </div>
        </v-card>
    </v-dialog>
</template>

<script>
  import {getSupplementalContent} from "../utilities/api";
  import SupplementalContentCard from "./SupplementalContentCard";

  export default {
    name: "SectionResources",
    components: {SupplementalContentCard},
    props:{
      title: String,
      part: String,
      section: String,
    },
    data () {
      return {
        dialog: false,
        notifications: false,
        sound: true,
        widgets: false,
        selectedCategory: [],
        content:[]
      }
    },
    async created() {
        try {
            this.content = await getSupplementalContent(this.title, this.part, [this.section], null );
        } catch (error) {
            console.error(error);
        }
    },
    computed:{
      availableCategories: function(){
        return this.content.map(category => category.name)
      },
      availableContent: function (){
        if (this.selectedCategory.length > 0){
          return this.content.filter(category => this.selectedCategory.indexOf(category.name) >= 0)
        }
        else{
          return this.content
        }
      }
    }
  }

</script>

<style>
.supplemental-content-category-title{
  font-size:22px;
  font-weight:bold;
}
.supplemental-content-subcategory-title{
  font-size:18px;

}
.centered-container{
  width:90%;
  margin:auto;
}

.flex-row-container {
    display: flex;
    flex-wrap: wrap;
    align-items: stretch;
    justify-content: left;
    margin-bottom: 40px;
}
.flex-row-container > .flex-row-item {
    flex: 1 1 30%; /*grow | shrink | basis */
    margin: 10px;
    max-width:30%;
}
.close-button{
  float:right;
}

.wrapper {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 10px;
}
.one {
  grid-column: 1 / 3;
  grid-row: 1;
}
</style>