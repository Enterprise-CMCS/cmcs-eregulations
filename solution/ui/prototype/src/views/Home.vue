<template>
    <body class="ds-base site-homepage">
        <div id="app">
            <FlashBanner />
            <Header />
            <main class="homepage">
                <Hero />
                <div
                    id="main-content"
                    class="site-container homepage-main-content"
                >
                    <div class="ds-l-row">
                        <div id="homepage-toc" class="homepage-toc ds-l-col--8">
                            <template v-if="structure">
                                <TOC :structure="structure" />
                            </template>
                            <template v-else>
                                <div class="toc-container">
                                    <SimpleSpinner />
                                </div>
                            </template>
                        </div>

                        <aside class="homepage-updates ds-l-col--4">
                            <RecentChanges />
                        </aside>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    </body>
</template>

<script>
// @ is an alias to /src
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import Hero from "@/components/homepage/Hero.vue";
import RecentChanges from "@/components/RecentChanges.vue";
import SimpleSpinner from "legacy/eregs-component-lib/src/components/SimpleSpinner.vue";
import TOC from "@/components/homepage/Toc.vue";

import { getHomepageStructure } from "@/utilities/api";

export default {
    components: {
        FlashBanner,
        Footer,
        Header,
        Hero,
        RecentChanges,
        SimpleSpinner,
        TOC,
    },

    name: "Home",

    data() {
        return {
            structure: null,
        };
    },

    async created() {
        try {
            this.structure = await getHomepageStructure();
        } catch (error) {
            console.error(error);
        }
    },
};
</script>

<style></style>
