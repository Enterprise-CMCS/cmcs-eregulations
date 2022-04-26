<template>
    <v-list class="section-list">
        <v-list-item-group class="section-list-item-group">
            <v-list-item
                v-for="item in listItems"
                :key="item.identifier"
                @click="clickMethod"
                :data-value="item.identifier"
                class="section-list-item"
            >
                <span class="section-number">{{ item.label }} </span>
                <span class="section-text">{{ item.description }}</span>
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "SectionList",

    props: {
        filterEmitter: {
            type: Function,
            required: true,
        },
        listItems: {
            type: Array,
            required: true,
        },
    },

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "section",
                selectedIdentifier: e.currentTarget.dataset.value
            });
        },
    },

}
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.section-list-item {
    display: inline-block;
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 14px;

    .section-number {
        color: $dark_gray;
    }

    .section-text {
        color: $mid_gray;
    }
}
</style>

