<template>
    <div class="results-container">
        <div class="results-content">
            <hr class="top-rule" />
            <div class="results-count">{{ sortedContent.length }} Results</div>
            <template v-for="(item, idx) in sortedContent">
                <div class="category-labels" :key="item.category + idx">
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
                <div class="result-content-wrapper" :key="item.name + item.created_at">
                    <SupplementalContentObject
                        :key="item.created_at"
                        :name="item.name"
                        :description="item.description"
                        :date="item.date"
                        :url="item.url"
                    />
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";

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
            return this.content
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
                            item.category = category.name;
                            returnArr.push(item);
                        });
                    }

                    return returnArr;
                });
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },

    watch: {
        content: {
            async handler() {
                console.log(this.content);
            },
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
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
            margin-bottom: 40px;
        }
    }
}
</style>
