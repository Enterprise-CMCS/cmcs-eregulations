<template>
    <form
        :class="formClasses"
        action=""
    >
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

