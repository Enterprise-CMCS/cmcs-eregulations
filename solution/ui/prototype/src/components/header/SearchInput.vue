<template>
    <form :class="formClasses" action="">
            <v-text-field
              v-model="message"
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

<style>


.search-box .search-header input {
    border: none;
    flex: auto;
    background-position: right;
}


</style>

