<template>
    <h1>{{ direction }}</h1>
</template>

<script>
export default {
    name: "BottomNavBtn",

    components: {},

    props: {
        direction: {
            type: String,
            required: true,
            default: "forward",
        },
    },
}
</script>

<style></style>

