<script>
const getSectionLink = ({ section }) => `#${section.replace('.', '-')}`;

export default {
    getSectionLink,
};
</script>

<script setup>
defineProps({
    item: {
        type: Object,
        required: true,
    },
    selectedPart: {
        type: String,
        required: false,
        default: undefined,
    },
});
</script>

<template>
    <p class="context-banner__item">
        <template v-if="!selectedPart">
            <strong>
                <a :href="getSectionLink({section: item.section})">§ {{ item.section }}</a>:
            </strong>
            <span v-sanitize-html="item.html" />
        </template>
        <template v-else>
            <span v-sanitize-html="item.html" />
        </template>
    </p>
</template>
