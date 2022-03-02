<template>
    <div style="margin: 15px 0px" class="list-item">
        <a :href="supplementalContent.url" target="_blank">
            <div class="supplemental-content__title">
                {{ formattedDate }}{{ supplementalContent.name ? ` | ${supplementalContent.name}` : "" }}
            </div>
            <div class="supplemental-content__text">
                {{ supplementalContent.description }}
            </div>
        </a>
    </div>
</template>

<script>
export default {
    name: "SupplementalContentList",
    props: {
        supplementalContent: Object,
    },
    computed: {
        formattedDate: function () {
            const date = new Date(this.supplementalContent.updated_at);
            const options = { year: "numeric", month: "long", day: "numeric" };
            return new Intl.DateTimeFormat("en-US", options).format(date);
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.list-item a {
    text-decoration: none;
}

.supplemental-content__title {
    font-size: 15px;
    line-height: 20px;
    font-weight: bold;
    color: #046791;
    word-break: normal;
}
.supplemental-content__text {
    font-size: 15px;
    color: #046791;
    width: 90%;
}
</style>
