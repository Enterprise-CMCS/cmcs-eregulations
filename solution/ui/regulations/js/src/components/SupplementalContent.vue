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

import {
    getSupplementalContentByCategory,
    v3GetSupplementalContent,
    getSubPartsForPart,
    getSubpartTOC
} from "../../api";
import { EventCodes, formatResourceCategories } from "../../utils";

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
                return [];
            },
        },
        getSupplementalContent: {
            type: Function,
            required: false,
            default: v3GetSupplementalContent,
        },
        getSupplementalContentByCategory: {
            type: Function,
            required: false,
            default: getSupplementalContentByCategory,
        },
        requested_categories: {
            type: String,
            required: false,
            default: "",
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
            let section = window.location.hash.substring(1).replace("-", ".");
            if (section.includes("-")) {
                // eslint-prefer-destructuring, kinda cool
                [section] = section.split("-");
            }
            if (isNaN(section)) {
                location = `locations=${this.title}.${this.part}.${section}`
            }
            else {
                location = `locations=${this.title}.${section}`
                this.selectedPart = `§ ${section}`;
        }
        } else {
            this.fetch_content(this.title, this.part);
        }
        this.fetch_content(this.title, this.part, location)
    },

    mounted() {
        this.$root.$on(EventCodes.SetSection, (args) => {
            this.selectedPart = args.section;
        });
        this.categories = getDefaultCategories();
    },

    methods: {
        async fetch_content(title, part, location) {
            try {
                if (this.requested_categories.length > 0) {
                    // todo convert this to V3 API
                    this.categories =
                        await this.getSupplementalContentByCategory(
                            this.api_url,
                            this.requested_categories.split(",")
                        );
                } else {
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
                }
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
        async get_location_string(){
            const sections = await getSubpartTOC(this.api_url, this.title, this.part, this.subparts[0])
            this.joined_locations= sections.reduce((previousValue, section) =>  `${previousValue}locations=${this.title}.${this.part}.${section.identifier[1]}&`, "")+ `locations=${this.title}.${this.part}.${this.subparts[0]}`;
        },
        clearSection() {
            console.log("Clearing Section");
            this.selectedPart = undefined;
            this.location= undefined;
        },
    },
};
</script>