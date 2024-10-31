<script setup>
const props = defineProps({
    searchQuery: {
        type: String,
        default: "",
    },
    showApology: {
        type: Boolean,
        default: false,
    },
    surveyUrl: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <div class="error-msg__container">
        <span class="error__msg" data-testid="error__msg">
            <span v-if="showApology" class="error__msg--apology"
                >Sorry, we’re unable to display results<span
                    v-if="searchQuery"
                    class="error__msg--query"
                >
                    for <strong>{{ searchQuery }}</strong></span
                >
                right now.
            </span>
            <span class="error-msg__common"
                >Please try a different query, try again later, or
                <a :href="surveyUrl" target="_blank" rel="noopener noreferrer"
                    >let us know</a
                >.</span
            ></span
        >
    </div>
</template>
