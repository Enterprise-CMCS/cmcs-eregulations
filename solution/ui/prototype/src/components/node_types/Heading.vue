<template>
    <h3 class="heading1">{{ node.content }}</h3>
</template>

<script>
export default {
    name: 'Heading',

    props: {
        node: {
            type: Object,
            required: true
        }
    }
}
</script>

<style>

</style>

