<template>
    <div class="nav-container" role="main">
        <div class="content">
            <h1>{{ title }}</h1>
            <slot name="description" />
            <slot name="input" />
            <slot name="filters" />
        </div>
    </div>
</template>

<script>
export default {
    name: "BannerComponent",

    components: {},

    props: {
        title: {
            type: String,
            required: true,
        },
    },
};
</script>
