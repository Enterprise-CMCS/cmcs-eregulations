<script setup>
const iconTypesDict = {
    "public_link": "users",
    "internal_file": "key",
};

const props = defineProps({
    iconType: {
        type: String,
        required: true,
    },
    docType: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="doc-type__label">
        <i :class="`fa fa-${iconTypesDict[iconType]}`"></i>
        {{ docType }}
    </div>
</template>
