<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <splitpanes>
              <pane min-size="30">
                <div style="width: 100%; margin: 20px">
<ResourceFilters /></div>
              </pane>
                <pane min-size="30">
                    <h1>Resources</h1>
                </pane>
            </splitpanes>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import ResourceFilters from "../components/ResourcesPage/ResourceFilters.vue"
export default {
    name: "ResourcePage",
    components: {
        FlashBanner,
        Header,
        Footer,
        Splitpanes,
        Pane,
        ResourceFilters,

    },
    data: () => ({
        items: ["foo", "bar", "fizz", "buzz", "fizzbuzz", "foobar"],
        value: ["foo", "bar", "fizz"],
    }),
};
</script>
<style>
</style>

