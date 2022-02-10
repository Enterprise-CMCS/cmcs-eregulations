<template>
    <h1>{{ title }} {{ part }}</h1>
</template>

<script>
export default {
    name: "Part",

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
        }
    },

    created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
                this.loadPart();
            }
        )
    }
}
</script>

<style>

</style>

