<template>
    <form :class="formClasses" action="">
        <button class="search-chevron">
            <p class="fa fa-chevron-down"></p>
        </button>
        <input type="search" name="q" placeholder="Search Regulations" />
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
.search-box input {
    border: none;
    flex: auto;
    padding: 30px;
    background-image: url(https://cdn2.hubspot.net/hubfs/4004166/bioticresearch_website_assets/images/search_icon.png);
    background-position: right;
}
.search-chevron p {
    background-color: #ddf5fd;
    font-size: 16px;
}
</style>

