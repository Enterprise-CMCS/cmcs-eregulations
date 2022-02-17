<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <PartNav :title="title" :part="part" :partLabel="partLabel">
                <v-tabs v-model="tab">
                    <v-tab v-for="item in tabsShape" :key="item.label">
                        {{ item.label }}
                    </v-tab>
                </v-tabs>
            </PartNav>
            <v-tabs-items v-model="tab">
                <template v-for="(item, index) in tabsContent">
                    <v-tab-item v-if="item" :key="index">
                        {{ item }}
                    </v-tab-item>
                    <v-tab-item v-else :key="index">
                        <SimpleSpinner />
                    </v-tab-item>
                </template>
            </v-tabs-items>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import PartNav from "@/components/part/PartNav.vue";
import SimpleSpinner from "legacy/js/src/components/SimpleSpinner.vue";

import { getPart } from "@/utilities/api";

export default {
    components: {
        FlashBanner,
        Footer,
        Header,
        PartNav,
        SimpleSpinner,
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            structure: null,
            partLabel: "",
            tab: 0,
            tabsShape: [
                {
                    label: "Table of Contents",
                    value: "tocContent",
                    type: "button",
                },
                {
                    label: "Part",
                    value: "partContent",
                    type: "button",
                },
                {
                    label: "Subpart",
                    value: "subpart",
                    type: "dropdown",
                    options: [],
                },
                {
                    label: "Section",
                    value: "section",
                    type: "dropdown",
                    options: [],
                },
            ],
        };
    },

    computed: {
        tocContent() {
            return this.structure?.toc ?? null;
        },
        partContent() {
            return "Part";
        },
        tabsContent() {
            return [this.tocContent, this.partContent, null, null];
        },
    },

    async created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
            }
        );

        try {
            this.structure = await getPart(this.title, this.part);
            this.partLabel = this.structure?.toc?.label_description ?? "N/A";
        } catch (error) {
            console.error(error);
        }
    },

    updated() {
        this.$nextTick(function () {
            console.log(this.tab);
            console.log(this.tabsContent);
        });
    },
};
</script>

<style></style>
