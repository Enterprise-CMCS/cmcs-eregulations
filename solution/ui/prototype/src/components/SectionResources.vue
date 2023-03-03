<template>
    <div
        class="footer-panel"
        :class="{ fullHeight: !collapsed, halfHeight: collapsed }"
    >
        <div class="toggle-btns-group">
            <v-btn-toggle>
                <v-btn @click="collapse" v-if="collapsed" class="toggle-btn">
                    <v-icon x-large>mdi-chevron-up</v-icon>
                    Expand
                </v-btn>
                <v-btn @click="collapse" v-else class="toggle-btn">
                    <v-icon x-large>mdi-chevron-down</v-icon>
                    Collapse
                </v-btn>

                <v-btn @click="$emit('close')" class="toggle-btn">
                    <v-icon x-large>mdi-close</v-icon>
                    Close
                </v-btn>
            </v-btn-toggle>
        </div>
        <div class="footer-panel-content-container">
            <div class="title-container" style="margin-bottom: 25px">
                <span class="subsection">§</span>
                <span class="resource-title"> {{ titleLabel }} Resources </span>
                <v-btn text @click="routeToResources" class="show-all-btn">
                    View All Resources
                </v-btn>
            </div>
            <div class="wrapper">
                <div class="one">
                    <v-text-field
                        solo
                        placeholder="Search Resources"
                        append-icon="mdi-magnify"
                    />
                </div>
                <div style="grid-column: 3; text-align: right">
                    <label class="filter-label">Filter by</label>
                </div>
                <div style="grid-column: 4 / 6">
                    <v-select
                        v-model="selectedCategory"
                        solo
                        :items="availableCategories"
                        multiple
                    />
                </div>
            </div>

            <v-divider class="hr-divider" />

            <div class="card-toggle-btns-group">
                <v-btn-toggle v-model="cardView" style="float: right">
                    <v-btn class="toggle-btn">
                        <v-icon>mdi-format-list-bulleted</v-icon>
                        List
                    </v-btn>

                    <v-btn class="toggle-btn">
                        <v-icon>mdi-view-grid</v-icon>
                        Grid
                    </v-btn>
                </v-btn-toggle>
            </div>
            <template v-if="isLoading">
                <SimpleSpinner />
            </template>
            <template v-else>
                <div
                    v-for="(category, idx) in availableContent"
                    :key="category.created_at"
                    :class="{ 'list-view': !cardView }"
                >
                    <div class="supplemental-content-category-title">
                        {{ category.name }}
                    </div>
                    <div v-if="cardView" class="flex-row-container">
                        <SupplementalContentCard
                            v-for="c in category.supplemental_content"
                            :key="c.created_at"
                            :supplemental-content="c"
                        />
                    </div>
                    <div v-else>
                        <SupplementalContentList
                            v-for="c in category.supplemental_content"
                            :key="c.created_at"
                            :supplemental-content="c"
                        />
                    </div>
                    <div
                        v-for="subcategory in category.sub_categories"
                        :key="subcategory.created_at"
                    >
                        <div class="supplemental-content-subcategory-title">
                            {{ subcategory.name }}
                        </div>
                        <div v-if="cardView" class="flex-row-container">
                            <SupplementalContentCard
                                v-for="c in subcategory.supplemental_content"
                                :key="c.created_at"
                                :supplemental-content="c"
                            />
                        </div>
                        <div v-else>
                            <SupplementalContentList
                                v-for="c in subcategory.supplemental_content"
                                :key="c.created_at"
                                :supplemental-content="c"
                            />
                        </div>
                    </div>
                    <v-divider v-if="availableContent.length - 1 != idx" class="hr-divider" />
                    <div class="btn-container" v-else>
                        <ResourcesBtn
                            :clickHandler="routeToResources"
                            label="All"
                            type="solid"
                        />
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import { getSupplementalContent } from "@/utilities/api";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import SimpleSpinner from "legacy/eregs-component-lib/src/components/SimpleSpinner.vue";
import SupplementalContentCard from "@/components/SupplementalContentCard";
import SupplementalContentList from "@/components/SupplementalContentList";

export default {
    name: "SectionResources",

    components: {
        ResourcesBtn,
        SimpleSpinner,
        SupplementalContentList,
        SupplementalContentCard,
    },

    props: {
        title: String,
        part: String,
        selectedIdentifier: Array,
        selectedScope: String,
        routeToResources: Function,
    },

    data() {
        return {
            dialog: false,
            notifications: false,
            sound: true,
            widgets: false,
            selectedCategory: [],
            content: [],
            cardView: 1,
            collapsed: true,
            isLoading: true,
        };
    },

    watch: {
        // whenever selected params changes, this function will run
        async selectedIdentifier(newSelectedIdentifier) {
            this.isLoading = true;
            try {
                this.content = await getSupplementalContent(
                    this.title,
                    this.part,
                    this.selectedScope,
                    newSelectedIdentifier,
                    null
                );
            } catch (error) {
                console.error(error);
            } finally {
                this.isLoading = false;
            }
        },
    },

    computed: {
        availableCategories: function () {
            return this.content.map((category) => category.name);
        },
        availableContent: function () {
            if (this.selectedCategory.length > 0) {
                return this.content.filter(
                    (category) =>
                        this.selectedCategory.indexOf(category.name) >= 0
                );
            } else {
                return this.content;
            }
        },
        titleLabel() {
            return this.selectedScope === "subpart"
                ? `${this.part} Subpart ${this.selectedIdentifier}`
                : this.selectedScope === "part"
                ? `${this.part}`
                : `${this.part}.${this.selectedIdentifier}`;
        },
    },

    async created() {
        try {
            this.content = await getSupplementalContent(
                this.title,
                this.part,
                this.selectedScope,
                this.selectedIdentifier,
                null
            );
        } catch (error) {
            console.error(error);
        } finally {
            this.isLoading = false;
        }
    },

    methods: {
        collapse: function () {
            this.collapsed = !this.collapsed;
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

.footer-panel {
    background-color: $lighter_gray;
    position: fixed;
    bottom: 0;
    width: 100%;
    z-index: 202;
    overflow: scroll;

    box-shadow: 0px 3px 10px 0px rgba(0, 0, 0, 0.5);
    -webkit-box-shadow: 0px 3px 10px 0px rgba(0, 0, 0, 0.5);
    -moz-box-shadow: 0px 3px 10px 0px rgba(0, 0, 0, 0.5);
}

.fullHeight {
    height: 100vh;
}

.halfHeight {
    height: 50vh;
}

.toggle-btns-group {
    position: absolute;
    right: 0;
    margin: 15px 0;

    .v-item-group.v-btn-toggle {
        background: $lighter_gray !important;
        border: none;

        button.v-btn.toggle-btn {
            border: none;
            background: $lighter_gray;
            padding: 10px 20px;

            &:first-child {
                border-right: 1px solid black;
            }

            span.v-btn__content {
                display: flex;
                flex-direction: column;
                letter-spacing: initial;
                color: $mid_gray;

                i.v-icon {
                    color: $mid_gray;
                }
            }
        }
    }

    .v-btn-toggle > .v-btn.toggle-btn.v-btn--active::before {
        opacity: 0;
    }
}

.card-toggle-btns-group {
    margin: 15px 0;

    .v-item-group.v-btn-toggle {
        background: $lighter_gray !important;
        border: none;

        button.v-btn.toggle-btn {
            border: none;
            background: $lighter_gray;
            height: 36px;
            border-radius: 2px;

            span.v-btn__content {
                font-size: 13px;
                display: flex;
                flex-direction: row;
                letter-spacing: initial;
                color: $mid_gray;
                text-transform: capitalize;

                i.v-icon {
                    color: $mid_gray;
                    margin-right: 5px;
                }
            }
        }
    }
}

.footer-panel-content-container {
    padding: 30px 120px;

    .title-container {
        display: flex;
        align-items: center;
        font-weight: 700;
        width: 90%;

        .subsection {
            font-size: 26px;
            margin: -5px 5px 0 0;
        }
        .resource-title {
            font-size: 30px;
        }

        .show-all-btn {
            color: $primary_link_color;
            letter-spacing: normal;
            text-decoration: underline;
            text-transform: capitalize;
            margin-left: 30px;

            .v-btn__content {
                font-size: 14px;
            }
        }
    }

    .btn-container {
        display: flex;
        justify-content: center;
    }
}

.hr-divider.v-divider {
    margin: 10px 0;
}

.supplemental-content-category-title {
    font-size: 22px;
    font-weight: bold;
}

.supplemental-content-subcategory-title {
    font-size: 18px;
    font-weight: 600;
    margin: 20px 0;
}
.centered-container {
    width: 90%;
    margin: auto;
}

.list-view {
    margin: 0 100px;
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
    max-width: 30%;
}

.wrapper {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 10px;
    align-items: baseline;
}

.filter-label {
    font-weight: 700;
}

.one {
    grid-column: 1 / 3;
    grid-row: 1;
}
</style>
