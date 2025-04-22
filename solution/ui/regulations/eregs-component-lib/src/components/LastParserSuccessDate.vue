<script setup>
import { ref, onMounted } from "vue";
import { getLastParserSuccessDate } from "utilities/api";
import SimpleSpinner from "./SimpleSpinner.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
});

const lastParserSuccess = ref("");

onMounted(() => {
    getLastParserSuccessDate({ apiUrl: props.apiUrl })
        .then((response) => {
            lastParserSuccess.value = response;
        })
        .catch(() => {
            lastParserSuccess.value = "N/A";
        });
});
</script>

<template>
    <span>
        <template v-if="lastParserSuccess">{{ lastParserSuccess }}</template>
        <span v-else class="spinner-span">
            <SimpleSpinner size="xs" />
        </span>
    </span>
</template>

<style>
.spinner-span {
    display: inline-block;
    padding: 0 5px;
}
</style>
