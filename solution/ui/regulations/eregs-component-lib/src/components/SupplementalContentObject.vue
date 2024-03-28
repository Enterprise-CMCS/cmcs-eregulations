<template>
    <div class="supplemental-content">
        <a
            class="supplemental-content-link"
            :href="url"
            target="_blank"
            rel="noopener noreferrer"
        >
            <span
                v-if="date"
                class="supplemental-content-date"
                :class="{
                    'supplemental-content-mid-bar': !isBlank(name) || division,
                }"
                >{{ formatDate(date) }}</span
            >
            <DivisionLabel
                v-if="docType === 'internal' && division"
                :division="division"
            />
            <span
                v-if="!isBlank(name)"
                class="supplemental-content-title"
                :class="{
                    'supplemental-content-external-link':
                        docType !== 'internal' && isBlank(description),
                }"
                >{{ name }}</span
            >
            <div
                v-if="!isBlank(description)"
                class="supplemental-content-description"
                :class="{
                    'supplemental-content-external-link':
                        docType !== 'internal',
                }"
            >
                <span
                    v-html="
                        description +
                        addFileTypeButton({
                            fileName,
                            url,
                            docType,
                        })
                    "
                />
            </div>
        </a>
    </div>
</template>

<script>
import { getFileTypeButton } from "utilities/utils";

import DivisionLabel from "./shared-components/results-item-parts/DivisionLabel.vue";

export default {
    name: "SupplementalContentObject",

    components: {
        DivisionLabel,
    },

    props: {
        name: {
            type: String,
            required: false,
            default: undefined,
        },
        description: {
            type: String,
            required: false,
            default: undefined,
        },
        date: {
            type: String,
            required: false,
            default: undefined,
        },
        division: {
            type: Object,
            required: false,
            default: null,
        },
        url: {
            type: String,
            default: undefined,
        },
        docType: {
            type: String,
            required: false,
            default: "external",
        },
        fileName: {
            type: String,
            required: false,
            default: undefined,
        },
    },

    methods: {
        isBlank(str) {
            return !str || /^\s*$/.test(str);
        },
        addFileTypeButton({ fileName, url, docType }) {
            if (docType !== "internal") {
                return "";
            }

            return getFileTypeButton({
                fileName,
                url,
            });
        },
        formatDate(value) {
            const date = new Date(value);
            const options = { year: "numeric", timeZone: "UTC" };
            const rawDate = value.split("-");
            if (rawDate.length > 1) {
                options.month = "long";
            }
            if (rawDate.length > 2) {
                options.day = "numeric";
            }
            const format = new Intl.DateTimeFormat("en-US", options);
            return format.format(date);
        },
    },
};
</script>

<style>
.search-highlight {
    font-weight: bold;
}
</style>
