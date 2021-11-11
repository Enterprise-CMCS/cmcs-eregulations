<template>
    <div class="show-more-button">
        <b>{{ buttonText }}</b> ({{ count }})
    </div>
</template>

<script>
export default {
    name: "show-more-button",
    props: {
        count: {
            type: Number,
            default: 1,
        },
        buttonText: {
            type: String,
            required: true
        }
    },
};
</script>
