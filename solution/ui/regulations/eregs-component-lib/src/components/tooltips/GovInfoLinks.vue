<template>
    <div class="gov-info-links-container">
        <div class="gov-info-links">
            <SimpleSpinner v-if="loading" size="medium" />
            <div v-else-if="govInfoLinks.length === 0" class="no-results">
                No results found.
            </div>
            <div v-else class="links-container">
                <a
                    v-for="(yearObj, index) in govInfoLinks"
                    :key="index"
                    :href="yearObj.link"
                    class="external"
                    target="_blank"
                    rel="noopener noreferrer"
                    >{{ yearObj.year }}</a
                >
            </div>
        </div>
        <div class="gov-info-source">
            Source: CFR Annual Edition from
            <a
                href="https://www.govinfo.gov/app/collection/cfr"
                class="external"
                target="_blank"
                rel="noopener noreferrer"
            >
                GovInfo</a
            >
            (1996–Present)
        </div>
    </div>
</template>

<script>
import { getGovInfoLinks } from "utilities/api";
import SimpleSpinner from "../SimpleSpinner.vue";

export default {
    name: "GovInfoLinks",

    components: {
        SimpleSpinner,
    },

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
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

    created() {
        getGovInfoLinks({
            apiUrl: this.apiUrl,
            filterParams: {
                title: this.title,
                part: this.part,
                section: this.section,
            },
        })
            .then((response) => {
                this.govInfoLinks = response.sort((a, b) => b.year - a.year);
            })
            .catch((error) => {
                console.error("Error", error);
                this.govInfoLinks = [];
            })
            .finally(() => {
                this.loading = false;
            });
    },

    data() {
        return {
            govInfoLinks: [],
            loading: true,
        };
    },
};
</script>
