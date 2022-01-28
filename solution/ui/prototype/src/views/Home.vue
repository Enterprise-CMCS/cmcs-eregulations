<template>
    <body class="ds-base site-homepage">
        <div id="app">
            <FlashBanner />
            <Header />
            <main class="homepage">
                <Hero />
            </main>
        </div>
    </body>
</template>

<script>
// @ is an alias to /src
import FlashBanner from "@/components/FlashBanner.vue";
import Header from "@/components/Header.vue";
import Hero from "@/components/homepage/Hero.vue";

export default {
    name: "Home",

    components: {
        FlashBanner,
        Header,
        Hero
    },
};
</script>

<style>

</style>
