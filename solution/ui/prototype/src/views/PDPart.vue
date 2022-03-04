<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <splitpanes>
                <pane min-size="30">
                    <left-column :title="title" :part="part" />
                </pane>
                <pane min-size="30">
                    <right-column :title="title" :part="part" />
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
import LeftColumn from "@/components/PDPart/LeftColumn";
import RightColumn from "../components/PDPart/RightColumn";

export default {
    name: "Part",
    components: {
        RightColumn,
        LeftColumn,
        FlashBanner,
        Footer,
        Header,
        Splitpanes,
        Pane,
    },

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            sections: [...Array(10).keys()], // This can go when we get real sections
            selectedSection: null,
        };
    },

    created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
            }
        );
    },
};
</script>

<style>
.splitpanes__pane {
    justify-content: left;
    align-items: flex-start;
    display: flex;
}

.splitpanes--vertical > .splitpanes__splitter {
    min-width: 6px;
    background: #a3e8ff;
}
</style>

