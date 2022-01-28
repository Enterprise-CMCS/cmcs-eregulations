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
                        <div
                            id="homepage-toc"
                            class="homepage-toc ds-l-col--8"
                        >
                            <div class="toc-container">
                                <h1>Title Placeholder</h1>

                                <p class="toc-external-ref">
                                    For subsequent subchapters (F-I), see
                                    <a
                                        href="https://www.ecfr.gov/current/title-42/chapter-IV"
                                        target="_blank"
                                        class="external"
                                        aria-label="link to Federal Register Title 42 Chapter 4"
                                    >Title 42 Chapter IV in eCFR</a>
                                </p>
                            </div>
                        </div>

                        <aside class="homepage-updates ds-l-col--4">
                            <RecentChanges />
                        </aside>
                    </div>
                </div>
            </main>
        </div>
    </body>
</template>

<script>
// @ is an alias to /src
import FlashBanner from "@/components/FlashBanner.vue";
import Header from "@/components/Header.vue";
import Hero from "@/components/homepage/Hero.vue";
import RecentChanges from "@/components/RecentChanges.vue";

export default {
    name: "Home",

    components: {
        FlashBanner,
        Header,
        Hero,
        RecentChanges
    },
};
</script>

<style></style>
