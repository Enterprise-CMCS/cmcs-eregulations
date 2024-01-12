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
                    'supplemental-content-mid-bar': !isBlank(name),
                }"
                >{{ date | formatDate }}</span
            >
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

export default {
    name: "SupplementalContentObject",

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

    filters: {
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
    },
};
</script>

<style>
.search-highlight {
    font-weight: bold;
}
</style>
