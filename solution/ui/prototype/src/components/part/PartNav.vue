<template>
    <div class="nav-container">
        <div class="content">
            <h1>{{ title }} CFR Part {{ part }} - {{ partLabel }}</h1>
        </div>
    </div>
</template>

<script>
export default {
    name: "PartNav",

    props: {
        title: {
            type: String,
            required: true
        },
        part: {
            type: String,
            required: true
        },
        partLabel: {
            type: String,
        }
    },
}
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.nav-container {
    overflow: auto;
    width: 100%;
    background: #eefafe;

    .content {
        max-width: $text-max-width;
        margin: 0 auto;

        h1 {
            margin-top: 55px;
            margin-bottom: 40px;
        }
    }

}

</style>

