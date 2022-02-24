<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <PartNav :title="title" :part="part" :partLabel="partLabel">
                <v-tabs
                    slider-size="5"
                    class="nav-tabs"
                    v-model="tab"
                    ref="tabs"
                >
                    <v-tab
                        v-for="item in tabsShape"
                        :key="item.label"
                        :disabled="item.disabled"
                    >
                        {{ item.label }}
                    </v-tab>
                </v-tabs>
            </PartNav>
            <div class="content-container">
                <div v-for="section in sections" v-bind:key="section">
                    <p>
                        I'm baby brunch banjo whatever, keffiyeh mustache
                        locavore migas kitsch shaman sustainable kinfolk hashtag
                        activated charcoal polaroid. Bespoke next level crucifix
                        waistcoat readymade. Gochujang bushwick microdosing cred
                        franzen umami. Tote bag pinterest man bun +1 master
                        cleanse ugh neutra sustainable tofu ramps copper mug put
                        a bird on it fingerstache chia.
                    </p>
                    <v-btn
                        color="primary"
                        outlined
                        v-on:click="selectedSection = section"
                    >
                        View Section Resources
                    </v-btn>
                </div>
                <v-tabs-items v-model="tab">
                    <v-tab-item v-for="(item, index) in tabsShape" :key="index">
                        <component
                            :is="item.component"
                            :structure="tabsContent[index]"
                        ></component>
                    </v-tab-item>
                </v-tabs-items>
            </div>
            <SectionResources
                v-bind:title="title"
                v-bind:part="part"
                v-bind:section="selectedSection"
                v-if="selectedSection"
                v-on:close="selectedSection = null"
            />
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
import SectionResources from "@/components/SectionResources.vue";

import { getPart } from "@/utilities/api";

export default {
    components: {
        SectionResources,
        FlashBanner,
        Footer,
        Header,
        PartContent,
        PartNav,
        PartToc,
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
                    disabled: false,
                },
                {
                    label: "Part",
                    value: "partContent",
                    type: "button",
                    component: "PartContent",
                    disabled: false,
                },
                {
                    label: "Subpart",
                    value: "subpart",
                    type: "dropdown",
                    disabled: true,
                },
                {
                    label: "Section",
                    value: "section",
                    type: "dropdown",
                    disabled: true,
                },
            ],
            sections: [...Array(10).keys()], // This can go when we get real sections
            selectedSection: null,
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
            console.log("updated", this.tab);
            // call onResize to fix tab highlight misalignment bug
            // https://github.com/vuetifyjs/vuetify/issues/4733
            this.$refs.tabs && this.$refs.tabs.onResize();
        });
    },
};
</script>

<style></style>
