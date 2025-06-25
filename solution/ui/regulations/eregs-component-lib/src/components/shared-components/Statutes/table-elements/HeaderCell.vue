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
            <template v-if="cellData.learnMoreUrl">
                <a
                    :href="cellData.learnMoreUrl"
                    class="cell__learn-more"
                    target="_blank"
                    rel="noopener"
                    style="color: #fff; text-decoration: underline;"
                >
                    {{ props.cellData.title }}
                </a>
            </template>
            <template v-else>
                {{ props.cellData.title }}
            </template>
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
