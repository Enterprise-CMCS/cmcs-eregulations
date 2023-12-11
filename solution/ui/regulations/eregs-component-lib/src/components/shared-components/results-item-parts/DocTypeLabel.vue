<script setup>
const iconTypesDict = {
    "external": "users",
    "internal": "key",
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
