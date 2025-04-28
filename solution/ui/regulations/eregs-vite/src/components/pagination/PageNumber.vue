<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const props = defineProps({
    currentPage: {
        type: Number,
        required: false,
        default: 1,
    },
    number: {
        type: Number,
        required: false,
        default: 1,
    },
});

const route = useRoute();

const numberClasses = computed(() => {
    return props.currentPage === props.number ? "selected" : "unselected";
});
</script>

<template>
    <li
        v-if="currentPage != number"
        class="page-number-li"
        :class="numberClasses"
    >
        <router-link
            :to="{
                name: view,
                query: { ...route.query, page: number },
            }"
        >
            {{ number }}
        </router-link>
    </li>
    <li
        v-else
        class="page-number-li current-page"
        :class="numberClasses"
    >
        {{ number }}
    </li>
</template>
