<template>
    <form :class="formClasses" action="">
        <v-text-field
            flat
            solo
            clearable
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

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.v-input__icon.v-input__icon--prepend button {
    background-color: $lighter_blue;
    border-radius: 3px;
}

.v-input__icon.v-input__icon--append button {
    color: $mid_blue;
}

.v-text-field.v-text-field--enclosed .v-input__slot {
    max-width: 160px;
}
</style>
