<template>
    <form class="search-input-form" :class="formClasses" action="">
        <v-text-field
            flat
            solo
            clearable
            class="header-search"
            label="Search"
            type="text"
            append-icon="mdi-magnify"
            prepend-icon="mdi-chevron-down"
            hide-details
            @click:prepend="toggle"
            @click:append="search"
        >
        </v-text-field>
    </form>
</template>

<script>
export default {
    name: "SearchInput",

    props: {
        type: {
            type: String,
            default: "",
        },
    },
    methods: {
        toggle() {
            console.log("toggle");
        },
        search() {
            console.log("search");
        },
    },
    computed: {
        formClasses() {
            return {
                "search-input": true,
                [this.type]: true,
            };
        },
    },
};
</script>

<style lang="scss" scoped>
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.search-input-form {
    .v-input__icon.v-input__icon--prepend button {
        background-color: $lighter_blue;
        border-radius: 3px;
    }

    .v-input__icon.v-input__icon--append button {
        color: $mid_blue;
    }
}
.header-search.v-text-field.v-text-field--enclosed {
    max-width: 200px;
}
</style>
