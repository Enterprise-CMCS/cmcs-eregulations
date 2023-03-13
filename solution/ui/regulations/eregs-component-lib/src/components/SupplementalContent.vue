<template>
    <div>
        <a
            v-if="selectedPart && subparts.length ===1"
            v-on:click="clearSection"
            class="show-subpart-resources"
        >
            <span class="bold">
                View All Subpart {{ subparts[0] }} Resources</span
            >
            ({{ resourceCount }})
        </a>
        <h2 id="subpart-resources-heading">
            {{ activePart }} Resources
        </h2>
        <div v-if="resource_display" class="resource_btn_container">
            <a :href="resourceLink" class=" default-btn action-btn search_resource_btn" >Search These Resources</a>
        </div>
        <div class="supplemental-content-container">
            <supplemental-content-category
                v-for="category in categories"
                :key="category.name"
                :name="category.name"
                :subcategory="false"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
                :is-fetching="isFetching"
                :is-fr-doc-category="category.is_fr_doc_category"
            >
            </supplemental-content-category>
            <simple-spinner v-if="isFetching"></simple-spinner>
        </div>
    </div>
</template>

<script>
import SimpleSpinner from "./SimpleSpinner.vue";
import SupplementalContentCategory from "./SupplementalContentCategory.vue";

import {
    v3GetSupplementalContent,
    getSubpartTOC
} from "../api";
import {EventCodes, flattenSubpart, formatResourceCategories} from "../utils";

function getDefaultCategories() {
    if (!document.getElementById("categories")) return [];

    const rawCategories = JSON.parse(
        document.getElementById("categories").textContent
    );
    const rawSubCategories = JSON.parse(
        document.getElementById("sub_categories").textContent
    );

    return rawCategories.map((c) => {
        const category = JSON.parse(JSON.stringify(c));
        category.sub_categories = rawSubCategories.filter(
            (subcategory) => subcategory.parent_id === category.id
        );
        return category;
    });
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
        resources_url: {
            type: String,
            required: false
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
            default: () => [],
        },
        subparts: {
            type: Array,
            required: false,
            default() {
                return [];
            },
        },
        getSupplementalContent: {
            type: Function,
            required: false,
            default: v3GetSupplementalContent,
        },
        resource_display:{
            type: Boolean,
            required: false,
            default: false
        },
    },

    data() {
        return {
            categories: [],
            isFetching: true,
            selectedPart: undefined,
            resourceCount: 0,
            joined_locations:""
        };
    },

    computed: {
        params_array: function () {
            return [
                ["sections", this.sections],
                ["subparts", this.subparts],
            ];
        },

        activePart: function () {
            if (this.selectedPart !== undefined) {
                return this.selectedPart;
            }
            return `Subpart ${this.subparts[0]}`;
        },

        resourceLink() {
            let qString = `${this.resources_url}\?title=${this.title}&part=${this.part}`

            if (this.activePart.includes("Subpart")){
                qString = `${qString}&subpart=${this.part}-${this.params_array[1][1]}` 
                let sections = `${this.part}-${this.sections.join(`,${this.part}-`)}`
                return `${qString}&section=${sections}`
            }
            else{
                const selection = this.activePart.split(" ")[1].replace(".","-");
                return `${qString}&section=${selection}`;
            }
        },
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
                this.fetch_content(
                    this.title,
                    this.part,
                    `locations=${this.title}.${this.part}.${
                        this.selectedPart.split(".")[1]
                    }`
                );
            } else {
                this.fetch_content(this.title, this.part);
            }
        },
    },

    created() {
        let location = ""
        if (window.location.hash) {
          location = this.parseHash(window.location.hash)
         } else {
            this.fetch_content(this.title, this.part);
        }
        this.fetch_content(this.title, this.part, location)
        window.addEventListener('hashchange', this.handleHashChange)
    },
    mounted() {
        this.$root.$on(EventCodes.SetSection, (args) => {
            this.selectedPart = args.section;
        });
        this.categories = getDefaultCategories();
    },
    destroyed() {
      window.removeEventListener("hashchange", this.handleHashChange);
    },

    methods: {
        handleHashChange() {
            const location = this.parseHash(window.location.hash)
            this.fetch_content(this.title, this.part, location)
        },
        parseHash(locationHash) {
            if (window.location.hash === "#main-content") return "";
            if (locationHash.toLowerCase().includes("appendix")) {
                this.selectedPart = undefined;
                return "";
            }

            let section = locationHash.substring(1).replace("-", ".");

            if (section.includes("-")) {
                // eslint-prefer-destructuring, kinda cool
                [section] = section.split("-");
            }

            if (Number.isNaN(section)) {
                return `locations=${this.title}.${this.part}.${section}`;
            }

            this.selectedPart = `§ ${section}`;
            return `locations=${this.title}.${section}`;
        },
        async fetch_content(title, part, location) {
            try {
                await this.get_location_string()
                const response = await v3GetSupplementalContent(
                    this.api_url,
                    {locations: location || this.joined_locations }
                );

                const subpart_response = await v3GetSupplementalContent(
                    this.api_url,
                    {locations: this.joined_locations}
                )
                if (!this.resourceCount) {
                    this.resourceCount = subpart_response.length;
                }

                this.categories = formatResourceCategories(response);
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
        async get_location_string(){
            const sections = await getSubpartTOC(this.api_url, this.title, this.part, this.subparts[0])
            const flatSections = flattenSubpart({children: sections})
            this.joined_locations = `${flatSections.children.reduce((previousValue, section) =>  `${previousValue}locations=${this.title}.${this.part}.${section.identifier[1]}&`, "") }locations=${this.title}.${this.part}.${this.subparts[0]}`;
        },
        clearSection() {
            console.log("Clearing Section");
            this.selectedPart = undefined;
            this.location= undefined;
        },
    },
};
</script>

<style lang="scss">
.resource_btn_container {
    padding: 5px 12px 5px 0px;
}
.search_resource_btn {
    width: fit-content;
    line-height: 18px;
    padding: 5px 12px 5px 12px;
    border: none;
    text-decoration: none;
}
a.search_resource_btn:visited{
    color:white
}
a.search_resource_btn:hover{
    color: white;
}
</style>
