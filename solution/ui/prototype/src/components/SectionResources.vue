<template>
    <div
        class="footer-panel"
        :class="{ fullHeight: !collapsed, halfHeight: collapsed }"
    >
        <div class="centered-container" style="margin-bottom: 25px">
            <b style="font-size: 30px">§{{ part }} Resources </b>
            <a style="font-size: 14px; margin-left: 15px">
                Show All Resources</a
            >
            <v-btn-toggle style="float: right">
                <v-btn @click="collapse" v-if="collapsed">
                    <v-icon>mdi-chevron-up</v-icon>
                    Expand
                </v-btn>
                <v-btn @click="collapse" v-else>
                    <v-icon>mdi-chevron-down</v-icon>
                    Collapse
                </v-btn>

                <v-btn @click="$emit('close')">
                    <v-icon>mdi-close</v-icon>
                    Close
                </v-btn>
            </v-btn-toggle>
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

<style>
.footer-panel {
    background-color: #f3f3f3;
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
