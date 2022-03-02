<template>
    <section>
        {{ node.content }}
    </section>
</template>

<script>
export default {
    name: "SectionAuthority",

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

