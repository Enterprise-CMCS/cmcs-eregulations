<template>
    <span>
        <template v-if="lastParserSuccess">{{ lastParserSuccess }}</template>
    </span>
</template>

<script>
import { getLastParserSuccessDate } from "../../api";
/*import InlineLoader from "@/components//InlineLoader.vue";*/

export default {
    name: "LastParserSuccessDate",

    components: {
        /*InlineLoader,*/
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
    },

    async created() {
        try {
            this.lastParserSuccess = await getLastParserSuccessDate(
                this.apiUrl,
                { title: 42 }
            );
        } catch (error) {
            console.error(error);
        }
    },

    data() {
        return {
            lastParserSuccess: "",
        };
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style></style>
