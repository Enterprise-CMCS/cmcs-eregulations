<template>
    <div class="toc">
        <div class="toc-header">
            <h2>Table of Contents</h2>
        </div>
        <div class="toc-body">
            {{ structure }}
        </div>
    </div>
</template>

<script>
export default {
    name: 'PartToc',

    props: {
        structure: {
            type: Object,
            required: false
        }
    }
}
</script>

<style>

</style>

