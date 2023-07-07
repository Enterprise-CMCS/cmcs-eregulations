<script setup>
import { DISPLAY_TYPES } from "../utils/enums";

const props = defineProps({
    cellData: {
        type: Object,
        required: true,
    },
    displayType: {
        validator: (value) => DISPLAY_TYPES.includes(value),
        required: false,
        default: "table",
    },
});
</script>

<template>
    <th
        class="row__cell row__cell--header"
        :class="{
            'row__cell--primary': cellData.primary,
            'row__cell--secondary': cellData.secondary,
        }"
    >
        <div class="cell__title">
            {{ cellData.title }}
        </div>
        <template v-if="cellData.subtitles">
            <div
                v-for="(subtitle, i) in cellData.subtitles"
                :key="`${displayType}-subtitle-${i}`"
                class="cell__subtitle"
            >
                {{ subtitle }}
            </div>
        </template>
    </th>
</template>
