<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <h1>{{ title }} {{ part }}</h1>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";

export default {
    components: {
        FlashBanner,
        Footer,
        Header
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
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

