<template>
    <form :class="formClasses" action="">
        <v-text-field
            flat
            solo
            clearable
            class="removethis"
            label="Search"
            type="text"
            append-icon="mdi-magnify"
            prepend-icon="mdi-chevron-down"
            hide-details
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

<style scoped>
.v-input >>>input{
    border:none;
}
</style>

