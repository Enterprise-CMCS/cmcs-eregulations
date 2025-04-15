<script setup>
defineProps({
    cellData: {
        type: Object,
        required: true,
    },
    statute: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <td
        class="row__cell row__cell--body"
        :class="{
            'row__cell--primary': cellData.header.primary,
            'row__cell--secondary': cellData.header.secondary,
        }"
    >
        <template v-if="cellData.body.primary">
            <div class="cell__title">
                {{ cellData.body.title(statute) }}
            </div>
            <div class="cell__usc-label">
                {{ cellData.body.label(statute) }}
            </div>
            <div class="cell__name">
                {{ cellData.body.name(statute) }}
            </div>
        </template>
        <template v-else>
            <a
                v-if="cellData.body.url(statute)"
                :class="cellData.body.type"
                :href="cellData.body.url(statute)"
                target="_blank"
                rel="noopener noreferrer"
            >
                <span class="table-link__span">{{ cellData.body.text(statute) }}</span>
                <span
                    v-if="cellData.body.url(statute) && cellData.body.type === 'pdf'"
                    class="result__link--file-type"
                >PDF</span>
            </a>
            <span v-else :data-testid="statute.usc + '-none'">None</span>
        </template>
    </td>
</template>
