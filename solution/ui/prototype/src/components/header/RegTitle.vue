<template>
    <div
        v-if="part"
        class="reg-title"
    >
        <!-- TODO: add a link to the regulation -->
    </div>
</template>

<script>
export default {
    name: "RegTitle",

    props: {
        part: {
            type: Boolean,
            default: false,
        },
    },
};
</script>

<style></style>
