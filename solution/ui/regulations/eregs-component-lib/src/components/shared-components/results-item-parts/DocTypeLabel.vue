<script setup>
import { DOCUMENT_TYPES_MAP } from "utilities/utils";

const iconTypesDict = {
    Public: "users",
    Internal: "key",
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
        <i :class="`fa fa-${iconTypesDict[DOCUMENT_TYPES_MAP[iconType]]}`" />
        {{ docType }}
    </div>
</template>
