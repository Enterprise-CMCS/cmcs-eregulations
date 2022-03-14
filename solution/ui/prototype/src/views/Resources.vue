<template>
    <body class="ds-base">
        <div id="app">
            <Header />
            <ResourcesNav :resourcesDisplay="resourcesDisplay">
                <p>search input goes here</p>
            </ResourcesNav>
        </div>
    </body>
</template>

<script>
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import ResourcesNav from "@/components/resources/ResourcesNav.vue";

export default {
    name: "Resources",

    components: {
        Footer,
        Header,
        ResourcesNav,
    },

    props: {},

    data() {
        return {
            queryParams: this.$route.query,
            resourcesDisplay: this.$route.params.resourcesDisplay || "column",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },

    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
                console.log("toParams in watch", toParams);
            },
        },
        "$route.query": {
            async handler(toQueries, previousQueries) {
                // react to route changes...
                console.log("toQueries in watch", toQueries);
            },
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

$sidebar-top-margin: 40px;

#app {
    display: flex;
    flex-direction: column;
}

.content-container {
    display: flex;
    flex-direction: row;
}

.content-container-column {
    justify-content: center;
}

.content-container-sidebar {
    justify-content: space-between;
}
</style>
