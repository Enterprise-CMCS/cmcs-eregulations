<template>
    <h1>{{ label }}</h1>
</template>

<script>
export default {
    name: "TocTitle",

    props: {
        label: {
            type: String,
            required: true
        }
    }

}
</script>

<style>

</style>

