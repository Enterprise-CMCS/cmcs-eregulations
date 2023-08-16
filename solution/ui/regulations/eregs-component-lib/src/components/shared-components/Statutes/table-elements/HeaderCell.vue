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
    columnDates: {
        type: Object,
        required: false,
        default: () => {},
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
            {{ props.cellData.title }}
        </div>
        <template v-if="cellData.subtitles">
            <div
                v-for="(subtitle, i) in cellData.subtitles"
                :key="`${props.displayType}-subtitle-${i}`"
                class="cell__subtitle"
                :data-testid="`${props.cellData.testId}-subtitle-${i}`"
            >
                {{ subtitle(columnDates) }}
            </div>
        </template>
    </th>
</template>
