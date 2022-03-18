<template>
    <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
            <v-btn class="ds-c-field select-btn" v-bind="attrs" v-on="on">
                {{ label }}
            </v-btn>
        </template>
        <v-list>
            <v-list-item>
                <v-list-item-title>Test</v-list-item-title>
            </v-list-item>
            <v-list-item>
                <v-list-item-title>Longer title that is longer than the button</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script>
export default {
    name: "FancyDropdown",

    components: {},

    props: {
        label: {
            type: String,
            default: "Select",
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

    data() {
        return {
            dataProp: "value",
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
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.select-btn {
    background-image: url(#{$eregs-image-path}/arrow-both.svg);
    background-position: right center;
}
</style>
