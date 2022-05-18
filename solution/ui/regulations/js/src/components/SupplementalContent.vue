<template>
  <div>
    <a v-if="selectedPart" v-on:click="clearSection" style="color:#5B616B; font-size: 12px">
      <span class="bold"> View All Subpart {{subparts[0]}} Resources</span>  ({{resourceCount}})
    </a>
    <h2 v-if="!requested_categories" id="subpart-resources-heading">
      {{ activePart }} Resources
    </h2>
    <div class="supplemental-content-container">
        <supplemental-content-category
            v-for="category in categories"
            :key="category.name"
            :name="category.name"
            :subcategory="false"
            :description="category.description"
            :supplemental_content="category.supplemental_content"
            :sub_categories="category.sub_categories"
            :isFetching="isFetching"
        >
        </supplemental-content-category>
        <simple-spinner v-if="isFetching"></simple-spinner>
    </div>
  </div>
</template>

<script>
import SimpleSpinner from "./SimpleSpinner.vue";
import SupplementalContentCategory from "./SupplementalContentCategory.vue";

import {getSupplementalContentByCategory,  getSupplementalContentLegacy } from "../../api";
import {EventCodes} from "../../utils";

function reducer(previousValue, currentValue){
  return previousValue + currentValue.supplemental_content.length + currentValue.sub_categories.reduce(reducer, 0)
}

export default {
    components: {
        SupplementalContentCategory,
        SimpleSpinner,
    },

    props: {
        api_url: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        sections: {
            type: Array,
            required: false,
            default: [],
        },
        subparts: {
            type: Array,
            required: false,
            default() {
              return []
            },
        },
        getSupplementalContent: {
          type: Function,
          required: false,
          default: getSupplementalContentLegacy
        },
        getSupplementalContentByCategory:{
          type: Function,
          required: false,
          default: getSupplementalContentByCategory
        },
        requested_categories:{
          type: String,
          required: false,
          default: ""
        }
    },

    data() {
        return {
            categories: [],
            isFetching: true,
            selectedPart: undefined,
            resourceCount: 0
        };
    },

    computed: {
        params_array: function () {
            return [
                ["sections", this.sections],
                ["subparts", this.subparts],
            ];
        },
        joined_locations: function () {
            let output = "";
            this.params_array.forEach(function (param) {
                if (param[1].length > 0) {
                    const queryString = "&" + param[0] + "=";
                    output += queryString + param[1].join(queryString);
                }
            });
            return output;
        },
        activePart: function(){
          if (this.selectedPart !== undefined) {

            return this.selectedPart

          }
          return `Subpart ${this.subparts[0]}`
        }
    },

    watch: {
        sections() {
            this.categories = [];
            this.isFetching = true;
            this.fetch_content(this.title, this.part);
        },
        subparts() {
            this.categories = [];
            this.isFetching = true;
            this.fetch_content(this.title, this.part);
        },
        selectedPart() {
            this.categories = [];
            this.isFetching = true;
            if (this.selectedPart) {
              this.fetch_content(this.title, this.part, `&sections=${this.selectedPart.split('.')[1]}`);
            }
            else{
              this.fetch_content(this.title, this.part);
            }
        },
    },

    created() {
        this.fetch_content(this.title, this.part);
    },

    mounted() {
        this.$root.$on(EventCodes.SetSection, (args) => {
          this.selectedPart = args.section
        })
        if (!document.getElementById("categories")) return;

        const rawCategories = JSON.parse(
            document.getElementById("categories").textContent
        );
        const rawSubCategories = JSON.parse(
            document.getElementById("sub_categories").textContent
        );

        this.categories = rawCategories.map((c) => {
            const category = JSON.parse(JSON.stringify(c));
            category.sub_categories = rawSubCategories.filter(
                (subcategory) => subcategory.parent_id === category.id
            );
            return category;
        });
    },

    methods: {
        async fetch_content(title, part, location) {
            try {
                if (this.requested_categories.length > 0){
                    this.categories = await this.getSupplementalContentByCategory(
                        this.api_url,
                        this.requested_categories.split(",")
                    );
                }
                else {
                    this.categories = await this.getSupplementalContent(
                        this.api_url,
                        title,
                        part,
                        location || this.joined_locations
                    );

                    if (!this.resourceCount) {
                      this.resourceCount = this.categories.reduce(reducer, 0);
                    }
                }

            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
      clearSection(){
          console.log("Clearing Section")
          this.selectedPart = undefined
      }
    },
};
</script>
<style>
  .bold{
    font-weight: 600
  }
</style>