<template>
    <div class="flex-row-item">
        <a :href="supplementalContent.url" target="_blank">
            <v-card class="supplemental-content-card">
                <v-card-title>
                    <div class="supplemental-content__title">
                        {{ formattedDate }}
                        {{
                            supplementalContent.name
                                ? ` | ${supplementalContent.name}`
                                : ""
                        }}
                    </div>
                </v-card-title>
                <v-card-text>
                    <div class="supplemental-content__text">
                        {{ supplementalContent.description }}
                    </div>
                </v-card-text>
            </v-card>
        </a>
    </div>
</template>

<script>
export default {
    name: "SupplementalContentCard",
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

.flex-row-item a {
    text-decoration: none;
}

.supplemental-content-card {
    height: 100%;
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

    &::after {
        @include external-link;
    }
}

</style>
