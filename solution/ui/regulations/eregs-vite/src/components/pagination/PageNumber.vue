<template>
    <li
        v-if="currentPage != number"
        class="page-number-li"
        :class="numberClasses"
    >
        <router-link
            :to="{
                name: view,
                query: { ...$route.query, page: number },
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

<script>
export default {
    name: "PageNumber",

    components: {},

    props: {
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
    },
    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        numberClasses() {
            return this.currentPage == this.number ? "selected" : "unselected";
        },
    },
};
</script>
