<script setup>
import { computed, ref } from "vue";

import HomeBook from "spaComponents/svgs/home-book.vue";
import HomeClipboard from "spaComponents/svgs/home-clipboard.vue";
import HomeSearch from "spaComponents/svgs/home-search.vue";

const props = defineProps({
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
        variant="tonal"
    >
        <v-card-title>
            <div class="icon-card__title-container">
                <div>
                    <slot name="card-title">
                        Default Title
                    </slot>
                </div>
                <component
                    :is="iconComponents[props.iconType]"
                    class="icon-card__icon"
                />
            </div>
        </v-card-title>
        <v-card-text>
            <slot name="card-content">
                Default Content
            </slot>
        </v-card-text>
    </v-card>
</template>
