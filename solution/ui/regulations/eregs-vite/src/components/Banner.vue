<template>
    <div class="nav-container" role="main">
        <div class="content">
            <h1>{{ title }}</h1>
            <slot name="description"></slot>
            <slot name="input"></slot>
            <slot name="filters"></slot>
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

<style lang="scss">
.nav-container {
    overflow: auto;
    background: $lightest_blue;
    padding: 0 $spacer-5;

    @include screen-xl {
        padding: 0 $spacer-4;
    }

    .content {
        margin: 0 auto;
        max-width: $text-max-width;

        h1 {
            margin-top: 45px;
            margin-bottom: 15px;
        }

        p:last-of-type {
            margin-bottom: 30px !important;
        }
    }
}
</style>
