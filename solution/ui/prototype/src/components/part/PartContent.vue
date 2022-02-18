<template>
    <div class="content">
        <div class="content-header">
            <h2>Part Content</h2>
        </div>
        <div class="content-body">
            {{ structure }}
        </div>
    </div>
</template>

<script>
export default {
    name: 'PartContent',

    props: {
        structure: {
            type: Object,
            required: false
        }
    },

}
</script>

<style>

</style>

