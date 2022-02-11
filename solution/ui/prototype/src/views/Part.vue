<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <PartNav :title="title" :part="part" :partLabel="partLabel" />
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import PartNav from "@/components/part/PartNav.vue";

import { getPart } from "@/utilities/api";

export default {
    components: {
        FlashBanner,
        Footer,
        Header,
        PartNav
    },

    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            structure: null,
            partLabel: null,
        }
    },

    async created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
            }
        )

        try {
            this.structure = await getPart(this.title, this.part);
            this.partLabel = this.structure.toc.label_description;
        } catch (error) {
            console.error(error);
        }
    }
}
</script>

<style>

</style>

