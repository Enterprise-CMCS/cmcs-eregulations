<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <h1>{{ title }} {{ part }}</h1>
            <h2>Selected Section: {{this.selectedSection}}</h2>
            <div
              v-for="section in sections"
              v-bind:key="section"
            >
              <p>I'm baby brunch banjo whatever, keffiyeh mustache locavore migas kitsch shaman sustainable kinfolk hashtag activated charcoal polaroid.  Bespoke next level crucifix waistcoat readymade.  Gochujang bushwick microdosing cred franzen umami.  Tote bag pinterest man bun +1 master cleanse ugh neutra sustainable tofu ramps copper mug put a bird on it fingerstache chia.</p>
              <v-btn
                  color="primary"
                  outlined
                  v-on:click="selectedSection = section"
              >
                  View Section Resources
              </v-btn>
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
import SectionResources from "@/components/SectionResources.vue"

export default {
    components: {
      SectionResources,
        FlashBanner,
        Footer,
        Header
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            sections: [...Array(10).keys()], // This can go when we get real sections
            selectedSection: null,
        }
    },

    created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
            }
        )
    }
}
</script>

<style>

</style>

