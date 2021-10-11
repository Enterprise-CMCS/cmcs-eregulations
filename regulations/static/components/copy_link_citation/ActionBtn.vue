<template>
    <button class="action-btn default-btn">{{ label }}</button>
</template>
<script>
export default {
    name: "action-button",

    props: {
        label: String,
        required: true,
    },

    computed: {},

    methods: {},

    filters: {},
};
</script>
