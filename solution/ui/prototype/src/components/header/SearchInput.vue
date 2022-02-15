<template>
    <form
        :class="formClasses"
        action=""
    >   <button class='search-chevron'><p class="fa fa-chevron-down"></p></button>
        <input
            type="search"
            name="q"
            placeholder="Search Regulations"
        />
               
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
    }
}
</script>

<style>

</style>

