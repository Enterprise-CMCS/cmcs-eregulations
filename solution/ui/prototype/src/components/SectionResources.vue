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
        <div class="centered-container" style="margin-bottom: 25px">
            <b style="font-size: 30px">§{{ titleLabel }} Resources </b>
            <a style="font-size: 14px; margin-left: 15px">
                Show All Resources</a
            >
        </div>
        <div class="wrapper centered-container">
            <div class="one">
                <v-text-field
                    solo
                    placeholder="Search Resources"
                    append-icon="mdi-magnify"
                />
            </div>
            <div style="grid-column: 3; text-align: right">
                <label>Filter By:</label>
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
        <v-divider />

        <v-btn-toggle v-model="cardView" style="float: right">
            <v-btn>
                <v-icon>mdi-format-list-bulleted</v-icon>
                List
            </v-btn>

            <v-btn>
                <v-icon>mdi-view-grid</v-icon>
                Grid
            </v-btn>
        </v-btn-toggle>
        <div
            v-for="category in availableContent"
            :key="category.name"
            class="centered-container"
        >
            <div class="supplemental-content-category-title">
                {{ category.name }}
            </div>
            <div v-if="cardView" class="flex-row-container">
                <SupplementalContentCard
                    v-for="c in category.supplemental_content"
                    :key="c.url"
                    :supplemental-content="c"
                />
            </div>
            <div v-else>
                <supplemental-content-list
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
                <div v-if="cardView" class="flex-row-container">
                    <SupplementalContentCard
                        v-for="c in subcategory.supplemental_content"
                        :key="c.url"
                        :supplemental-content="c"
                    />
                </div>
                <div v-else>
                    <supplemental-content-list
                        v-for="c in subcategory.supplemental_content"
                        :key="c.url"
                        :supplemental-content="c"
                    />
                </div>
            </div>
            <v-divider />
        </div>
    </div>
</template>

<script>
import { getSupplementalContent } from "../utilities/api";
import SupplementalContentCard from "./SupplementalContentCard";
import SupplementalContentList from "./SupplementalContentList";

export default {
    name: "SectionResources",
    components: { SupplementalContentList, SupplementalContentCard },
    props: {
        title: String,
        part: String,
        selectedIdentifier: String,
        selectedScope: String,
    },
    watch: {
        // whenever selected params changes, this function will run
        async selectedIdentifier(newSelectedIdentifier) {
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
            }
        },
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
        };
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
}

.supplemental-content-category-title {
    font-size: 22px;
    font-weight: bold;
}

.supplemental-content-subcategory-title {
    font-size: 18px;
}
.centered-container {
    width: 90%;
    margin: auto;
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
}
.one {
    grid-column: 1 / 3;
    grid-row: 1;
}
</style>
