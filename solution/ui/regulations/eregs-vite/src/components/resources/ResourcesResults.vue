<template>
    <div class="results-container">
        <div class="results-content">
            <hr class="top-rule" />
            <div class="results-count">
                <span v-if="isLoading">Loading...</span>
                <span v-else>{{ content.length }} Results</span>
            </div>
            <div v-if="!isLoading">
                <template v-for="(item, idx) in filteredContent">
                    <div :key="item.created_at + idx">
                        <div class="category-labels">
                            <div
                                class="result-label category-label"
                            >
                               {{ item.category.parent ? item.category.parent.name : item.category.name}}
                            </div>
                            <div
                                v-if="item.category.parent"
                                class="result-label subcategory-label"
                            >
                               {{ item.category.name }}
                            </div>
                        </div>
                        <div class="result-content-wrapper">
                            <SupplementalContentObject
                                :name="item.name"
                                :description="
                                    item.descriptionHeadline || item.description
                                "
                                :date="item.date"
                                :url="item.url"
                            />
                        </div>
                        <div class="related-sections">
                            <span class="related-sections-title">
                                Related Regulation<span
                                    v-if="item.locations.length > 1"
                                    >s</span
                                >:
                            </span>
                            <span v-if="item.locations.length > 1">§§ </span>
                            <span v-else>§ </span>
                            <template v-for="(location, i) in item.locations">
                                <span
                                    :key="location.display_name + i"
                                    class="related-section-link"
                                >
                                    <a
                                        :href="
                                            location
                                                | locationUrl(
                                                    partsList,
                                                    partsLastUpdated
                                                )
                                        "
                                    >
                                        {{
                                            location
                                                | locationLabel
                                        }}
                                    </a>
                                    <span v-if="i + 1 != item.locations.length">
                                        |
                                    </span>
                                </span>
                            </template>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";
import _uniqBy from "lodash/uniqBy";
import _has from "lodash/has";

export default {
    name: "ResourcesResults",

    components: {
        SupplementalContentObject,
    },

    filters: {
        locationLabel(value) {

            return value.type.toLowerCase() === 'section' ? `${value.part}.${value.section_id}` : `${value.part} Subpart ${value.subpart_id}`
        },
        locationUrl(value, partsList, partsLastUpdated) {
            // getting parent and partDate for proper link to section
            // e.g. /42/433/Subpart-A/2021-03-01/#433-10
            // is not straightforward with v2.  See below.
            // Thankfully v3 will add "latest" for date
            // and will better provide parent subpart in resource locations array.
            const {part, section_id, type, title, subpart_id} = value;
            const base =
                import.meta.env.VITE_ENV && import.meta.env.VITE_ENV !== "prod"
                    ? `/${import.meta.env.VITE_ENV}`
                    : "";
            const partDate = `${partsLastUpdated[part]}/`;

            // early return if related regulation is a subpart and not a section
            if (type.toLowerCase() === "subpart") {
                return `${base}/${title}/${part}/Subpart-${subpart_id}/${partDate}`;
            }
            const partObj = partsList.find(
                (parts) => parts.name == part
            );
            const subpart = partObj.sections[section_id]

            // todo: Figure out which no subpart sections are invalid and which are orphans
            return subpart ?
                `${base}/${title}/${part}/Subpart-${subpart}/${partDate}#${part}-${section_id}`
                :
                `${base}/${title}/${part}/${partDate}#${part}-${section_id}`

        },
    },

    props: {
        content: {
            type: Array,
            required: false,
            default() {
              return []
            },
        },
        isLoading: {
            type: Boolean,
            required: false,
            default: false,
        },
        partsList: {
            type: Array,
            required: true,
            default: () => [],
        },
        partsLastUpdated: {
            type: Object,
            required: true,
            default: () => {},
        },
    },

    data() {},

    computed: {
      filteredContent(){
        return this.content.map(item => {
          const copiedItem = JSON.parse(JSON.stringify(item))
          copiedItem.locations = item.locations.filter(location => this.partsLastUpdated[location.part])
          return copiedItem
        })
      }
    },
};
</script>

<style lang="scss">
.results-container {
    overflow: auto;
    width: 100%;
    margin-bottom: 30px;
    .results-content {
        max-width: $text-max-width;
        margin: 0 auto;
        .top-rule {
            border-top: 1px solid #dddddd;
            margin-bottom: 30px;
        }
        .results-count {
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 40px;
        }
        .category-labels {
            margin-bottom: 5px;
            .result-label {
                font-size: 11px;
                display: inline;
                margin-right: 5px;
                background: #e3eef9;
                border-radius: 3px;
                padding: 2px 5px 3px;
                &.category-label {
                    font-weight: 600;
                }
            }
        }
        .result-content-wrapper {
            margin-bottom: 20px;
            .supplemental-content a.supplemental-content-link {
                .supplemental-content-date,
                .supplemental-content-title,
                .supplemental-content-description {
                    font-size: 18px;
                }
            }
        }
        .related-sections {
            margin-bottom: 40px;
            font-size: 12px;
            color: $mid_gray;
            .related-sections-title {
                font-weight: 600;
                color: $dark_gray;
            }
            a {
                text-decoration: none;
            }
        }
    }
}
</style>