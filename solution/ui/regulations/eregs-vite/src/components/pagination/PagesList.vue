<script setup>
import { computed } from "vue";
import PageNumber from "@/components/pagination/PageNumber.vue";

const props = defineProps({
    currentPage: {
        type: Number,
        required: false,
        default: 1,
    },
    pagesArray: {
        type: Array,
        required: false,
        default: () => [],
    },
});

const firstPage = computed(() => props.pagesArray[0]);

const frontFour = computed(() => {
    // slice of pages 2 through 5
    return props.pagesArray.slice(1, 5);
});

const shortMiddlePages = computed(() => {
    // three-page slice of page before current page,
    // current page, and page after current page
    return props.pagesArray.slice(props.currentPage - 2, props.currentPage + 1);
});

const allMiddlePages = computed(() => {
    // slice of all pages between first and last page
    return props.pagesArray.slice(1, -1);
});

const backFour = computed(() => {
    // slice of n - 5 to n - 1
    return props.pagesArray.slice(-5, -1);
});

const lastPage = computed(() => props.pagesArray[props.pagesArray.length - 1]);

const iterablePages = computed(() => {
    if (props.pagesArray.length > 7) {
        if (props.currentPage < 5) {
            return frontFour.value;
        }

        if (props.pagesArray.length - 3 <= props.currentPage) {
            return backFour.value;
        }

        if (props.pagesArray.length > props.currentPage) {
            return shortMiddlePages.value;
        }
    }

    return allMiddlePages.value;
});
</script>

<template>
    <div class="list-container">
        <ul class="pages desktop-list">
            <PageNumber
                v-if="pagesArray.length > 0"
                :current-page="currentPage"
                :number="firstPage"
            />
            <li
                v-if="pagesArray.length > 7 && currentPage > 4"
                class="ellipses"
            >
                …
            </li>
            <PageNumber
                v-for="pageNum in iterablePages"
                :key="pageNum"
                :current-page="currentPage"
                :number="pageNum"
            />
            <li
                v-if="
                    pagesArray.length > 7 && pagesArray.length > currentPage + 3
                "
                class="ellipses"
            >
                …
            </li>
            <PageNumber
                v-if="pagesArray.length > 1"
                :current-page="currentPage"
                :number="lastPage"
            />
        </ul>
        <div class="mobile-list">
            Page <span class="mobile-page-number">{{ currentPage }}</span> of
            <span class="mobile-page-number">{{ lastPage }}</span>
        </div>
    </div>
</template>
