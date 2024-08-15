<template>
    <span>
        <template v-if="lastParserSuccess">{{ lastParserSuccess }}</template>
        <span v-else class="spinner-span">
            <SimpleSpinner size="xs" />
        </span>
    </span>
</template>

<script>
import { getLastParserSuccessDate } from "utilities/api";
import SimpleSpinner from "./SimpleSpinner.vue";

export default {
    name: "LastParserSuccessDate",

    components: {
        SimpleSpinner,
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
    },

    created() {
        getLastParserSuccessDate({ apiUrl: this.apiUrl })
            .then((response) => {
                this.lastParserSuccess = response;
            })
            .catch(() => {
                this.lastParserSuccess = "N/A";
            });
    },

    data() {
        return {
            lastParserSuccess: "",
        };
    },
};
</script>

<style>
.spinner-span {
    display: inline-block;
    padding: 0 5px;
}
</style>
