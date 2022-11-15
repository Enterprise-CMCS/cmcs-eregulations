<template>
    <body class="ds-base">
        <div id="searchApp" class="search-view">
            <Banner title="Search Results">
                <template #description>
                    <p>This site searches Title 42, Parts 400 and 430-460</p>
                    <p>{{ q }}</p>
                </template>
                <template #input>
                    <form class="search-form">
                        <v-text-field
                            id="main-content"
                            outlined
                            flat
                            solo
                            clearable
                            label="Search Regulations"
                            aria-label="Search Regulations"
                            type="text"
                            class="search-field shrink"
                            append-icon="mdi-magnify"
                            hide-details
                            dense
                        />
                    </form>
                </template>
            </Banner>
        </div>
    </body>
</template>

<script>
import Banner from "@/components/Banner.vue";

export default {
    name: "SearchView",

    components: {
        Banner,
    },

    props: {
        q: {
            type: String,
            required: false,
            default: "",
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

    data() {},

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {},
};
</script>

<style lang="scss">
#searchApp.search-view {
    display: flex;
    flex-direction: column;

    .search-form {
        .search-field {
            height: 40px;
            margin-bottom: 50px;
            .v-input__icon.v-input__icon--append button {
                color: $mid_blue;
            }
        }
    }
}
</style>
