<script setup>

import HomeBook from "spaComponents/svgs/home-book.vue";
import HomeClipboard from "spaComponents/svgs/home-clipboard.vue";
import HomeSearch from "spaComponents/svgs/home-search.vue";

defineProps({
    iconType: {
        type: String,
        required: true,
    },
});

const iconComponents = {
    book: HomeBook,
    clipboard: HomeClipboard,
    search: HomeSearch,
};

</script>

<template>
    <v-card
        class="icon-card"
        variant="outlined"
    >
        <v-card-title class="icon-card__header">
            <div class="icon-card__title-container">
                <div class="icon-card__title">
                    <slot name="card-title">
                        Default Title
                    </slot>
                </div>
                <div class="icon-card__icon">
                    <component
                        :is="iconComponents[iconType]"
                        class="icon-card__icon"
                    />
                </div>
            </div>
        </v-card-title>
        <v-card-text class="icon-card__content">
            <slot name="card-content">
                Default Content
            </slot>
        </v-card-text>
    </v-card>
</template>
