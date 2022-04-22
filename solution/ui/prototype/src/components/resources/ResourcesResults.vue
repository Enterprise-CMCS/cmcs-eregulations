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
                                Related Section<span v-if="item.locations.length > 1">s</span>:
                            </span>
                            <span v-if="item.locations.length > 1">§§ </span>
                            <span v-else>§ </span>
                            <span
                                v-for="(location, idx) in item.locations"
                                :key="location.display_name + idx"
                                class="related-section-link"
                            >
                                <router-link
                                    :to="{
                                        name: 'part',
                                        params: {
                                            title: location.title,
                                            part: location.part,
                                        },
                                    }"
                                >{{location.display_name | locationLabel}}</router-link>
                                <span v-if="idx + 1 != item.locations.length"> | </span>
                            </span>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";
import _uniqBy from "lodash/uniq";
import _has from "lodash/has";

export default {
    name: "ResourcesResults",

    components: {
        SupplementalContentObject,
    },

    props: {
        content: {
            type: Array,
            required: false,
            default: [],
        },
        isLoading: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        sortedContent() {
            let results = this.content
                .filter((category) => {
                    return (
                        category.supplemental_content?.length ||
                        category.sub_categories?.length
                    );
                })
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

    methods: {},

    filters: {
        locationLabel(value) {
            return value.substring(3);
        },
    },

    watch: {
        content: {
            async handler() {
                /*console.log(this.content);*/
            },
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

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
        }
    }
}
</style>
