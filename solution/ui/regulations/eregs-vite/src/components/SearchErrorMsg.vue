<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    searchQuery: {
        type: String,
        default: "",
    },
    surveyUrl: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <div class="error-msg__container">
        <span class="error__msg"
            >Sorry,
            <span class="error__msg--query" v-if="searchQuery"
                >we’re unable to display results for
                <strong>{{ searchQuery }}</strong> right now.
            </span>
            <span class="error-msg__common"
                ><span
                    data-testid="error-msg__common--first-letter"
                    :class="{ 'error-msg__common--first-letter': searchQuery }"
                    >t</span
                >he server is taking too long to respond. Please try a different
                query, try again later, or
                <a :href="surveyUrl" target="_blank" rel="noopener noreferrer"
                    >let us know</a
                >.</span
            ></span
        >
    </div>
</template>

<style></style>
