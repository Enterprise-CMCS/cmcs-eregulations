<template>
    <p class="effective-date-note">
        <span class="effective-date-note-header">{{ node.header }} </span>
        {{ node.content }}
    </p>
</template>

<script>
export default {
    name: "EffectiveDateNote",

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

