<template>
    <div class="results-container">
        <div class="results-content">
            <hr class="top-rule" />
            <div class="results-count">
                <span v-if="isLoading">Loading...</span>
                <span v-else>{{ sortedContent.length }} Results</span>
            </div>
            <div v-if="!isLoading">
                <template v-for="(item, idx) in sortedContent">
                    <div :key="item.created_at + idx">
                        <div class="category-labels">
                            <div
                                v-if="item.category"
                                class="result-label category-label"
                            >
                                {{ item.category }}
                            </div>
                            <div
                                v-if="item.sub_category"
                                class="result-label subcategory-label"
                            >
                                {{ item.sub_category }}
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
                                    v-if="partsLastUpdated[location.part]"
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
                                            location.display_name
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
            return value.substring(3);
        },
        locationUrl(value, partsList, partsLastUpdated) {
            // getting parent and partDate for proper link to section
            // e.g. /42/433/Subpart-A/2021-03-01/#433-10
            // is not straightforward with v2.  See below.
            // Thankfully v3 will add "latest" for date
            // and will better provide parent subpart in resource locations array.
            let parent = "";
            const base =
                import.meta.env.VITE_ENV && import.meta.env.VITE_ENV !== "prod"
                    ? `/${import.meta.env.VITE_ENV}`
                    : "";
            const partDate = `${partsLastUpdated[value.part]}/`;

            // early return if related regulation is a subpart and not a section
            if (value.display_name.includes("Subpart")) {
                const subpart = value.display_name
                    .split(" ")
                    .slice(2)
                    .join("-");
                return `${base}/42/${value.part}/${subpart}/${partDate}`;
            }

            const partAndSection = value.display_name.split(" ")[1];
            const section = partAndSection.split(".")[1];
            const partObj = partsList.find(
                (part) => part.name === value.part.toString()
            );
            if (partObj.sections) {
                const partSectionsDict = partObj.sections;
                parent =
                    partSectionsDict[section] &&
                    partSectionsDict[section] !== "orphan"
                        ? `Subpart-${partSectionsDict[section]}/`
                        : "";
            }
            const hash = `#${partAndSection.replace(/\./g, "-")}`;
            return `${base}/42/${value.part}/${parent}${partDate}${hash}`;
        },
    },

    props: {
        content: {
            type: Array,
            required: false,
            default: () => [],
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
        sortedContent() {
            let results = this.content
                .filter(
                    (category) =>
                        category.supplemental_content?.length ||
                        category.sub_categories?.length
                )
                .flatMap((category) => {
                    const returnArr = [];
                    if (category.sub_categories?.length) {
                        category.sub_categories.forEach((sub_category) => {
                            sub_category.supplemental_content.forEach(
                                (item) => {
                                    item.category = category.name;
                                    item.sub_category = sub_category.name;
                                    returnArr.push(item);
                                }
                            );
                        });
                    } else {
                        category.supplemental_content.forEach((item) => {
                            if (_has(category, "parent_category")) {
                                item.category = category.parent_category;
                                item.sub_category = category.name;
                            } else {
                                item.category = category.name;
                            }
                            returnArr.push(item);
                        });
                    }

                    return returnArr;
                });

            //remove duplicates
            results = _uniqBy(results, (item) => {
                return item.name;
            });

            return results;
        },
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
