<template>
    <li class="page-number-li">
        <router-link
            v-if="currentPage != number"
            :to="{
                name: view,
                query: { ...$route.query, page: number },
            }"
        >
            <span class="page-number" :class="numberClasses">
                {{ number }}
            </span>
        </router-link>
        <span v-else class="current-page">
            <span class="page-number" :class="numberClasses">
                {{ number }}
            </span>
        </span>
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

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

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

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style lang="scss" scoped>
li.page-number-li {
    display: inline-block;
    list-style: none;
    width: 44px;
    text-align: center;

    a {
        text-decoration: none;

        &:visited {
            color: $mid_blue;
        }
    }

    .page-number {
        min-width: 44px;

        &.selected {
            font-weight: bold;
        }
    }
}
</style>
