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
                <v-tab-item v-for="(item, index) in tabsShape" :key="index">
                    <component
                        :is="item.component"
                        :structure="tabsContent[index]"
                    ></component>
                </v-tab-item>
            </v-tabs-items>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import PartContent from "@/components/part/PartContent.vue";
import PartNav from "@/components/part/PartNav.vue";
import PartToc from "@/components/part/PartToc.vue";
import SimpleSpinner from "legacy/js/src/components/SimpleSpinner.vue";

import { getPart } from "@/utilities/api";

export default {
    components: {
        FlashBanner,
        Footer,
        Header,
        PartContent,
        PartNav,
        PartToc,
        SimpleSpinner,
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            structure: null,
            sections: [],
            tab: 1, // index 1, "Part"
            tabsShape: [
                {
                    label: "Table of Contents",
                    value: "tocContent",
                    type: "button",
                    component: "PartToc",
                },
                {
                    label: "Part",
                    value: "partContent",
                    type: "button",
                    component: "PartContent",
                },
                {
                    label: "Subpart",
                    value: "subpart",
                    type: "dropdown",
                },
                {
                    label: "Section",
                    value: "section",
                    type: "dropdown",
                },
            ],
        };
    },

    computed: {
        tocContent() {
            return this.structure?.[0];
        },
        partLabel() {
            return this.structure?.[0].label_description ?? "N/A";
        },
        partContent() {
            return this.structure?.[1];
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
        } catch (error) {
            console.error(error);
        }
    },

    updated() {
        this.$nextTick(function () {
            console.log(this.tab);
        });
    },
};
</script>

<style></style>
