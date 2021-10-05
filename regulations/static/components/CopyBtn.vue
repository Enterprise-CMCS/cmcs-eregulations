<template>
    <span
        :class="[className]"
        :title="title"
    >
        <i class="fa fa-link"></i>
        <span v-if="label">{{ label }}</span>
    </span>
</template>

<script>
export default {
    name: "copy-btn",

    props: {
        class: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        label: String,
    },

    data: function() {
        return {
            className: this.class,
            title: this.title
        }
    }
};
</script>
