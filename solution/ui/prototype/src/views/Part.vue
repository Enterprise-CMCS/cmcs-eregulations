<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <h1>{{ title }} {{ part }}</h1>
            <SectionResources
                v-bind:title="title"
                v-bind:part="part"
                v-bind:section="section"
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
            section: 10,
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

