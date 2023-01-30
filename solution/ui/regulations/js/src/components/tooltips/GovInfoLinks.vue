<template>
    <div class="gov-info-links-container">
        <div class="gov-info-links">
            <SimpleSpinner v-if="loading" size="medium" />
            <div v-else class="links-container">
                <a
                    v-for="(yearObj, index) in govInfoLinks"
                    :key="index"
                    :href="yearObj.link"
                    class="external"
                    target="_blank"
                >
                    {{ yearObj.year }}
                </a>
            </div>
        </div>
        <div class="gov-info-source">
            Section text is revised as of October 1st of each listed year. Link
            sources: <a href="https://www.govinfo.gov">GovInfo.gov</a>.
        </div>
    </div>
</template>

<script>
import { getGovInfoLinks } from "../../../api";
import SimpleSpinner from "../SimpleSpinner.vue";

export default {
    name: "GovInfoLinks",

    components: {
        SimpleSpinner,
    },

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        section: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {
        getGovInfoLinks({
            title: this.title,
            part: this.part,
            section: this.section,
        })
            .then((response) => {
                const reversedResponse = response.reverse();
                this.govInfoLinks = reversedResponse;
            })
            .catch((error) => {
                console.error("Error", error);
                this.govInfoLinks = [];
            })
            .finally(() => {
                this.loading = false;
            });
    },

    beforeMount() {},

    mounted() {
        console.log("this.title", this.title);
        console.log("this.part", this.part);
        console.log("this.section", this.section);
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            govInfoLinks: [],
            loading: true,
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style></style>
