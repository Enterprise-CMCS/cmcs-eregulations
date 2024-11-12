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

<script>
import PageNumber from "@/components/pagination/PageNumber.vue";

export default {
    name: "PagesList",

    components: {
        PageNumber,
    },

    props: {
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
    },

    computed: {
        firstPage() {
            return this.pagesArray[0];
        },
        frontFour() {
            // slice of pages 2 through 5
            return this.pagesArray.slice(1, 5);
        },
        shortMiddlePages() {
            // three-page slice of page before current page,
            // current page, and page after current page
            return this.pagesArray.slice(
                this.currentPage - 2,
                this.currentPage + 1
            );
        },
        allMiddlePages() {
            // slice of all pages between first and last page
            return this.pagesArray.slice(1, -1);
        },
        backFour() {
            // slice of n - 5 to n - 1
            return this.pagesArray.slice(-5, -1);
        },
        lastPage() {
            return this.pagesArray[this.pagesArray.length - 1];
        },
        iterablePages() {
            if (this.pagesArray.length > 7) {
                if (this.currentPage < 5) {
                    return this.frontFour;
                }

                if (this.pagesArray.length - 3 <= this.currentPage) {
                    return this.backFour;
                }

                if (this.pagesArray.length > this.currentPage) {
                    return this.shortMiddlePages;
                }
            }

            return this.allMiddlePages;
        },
    },
};
</script>
