<script setup>
import { DOCUMENT_TYPES_MAP, getFileTypeButton } from "utilities/utils";

const props = defineProps({
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
    uid: {
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
        default: "public_link",
    },
    fileName: {
        type: String,
        required: false,
        default: undefined,
    },
});

const isBlank = (str) => {
    return !str || /^\s*$/.test(str);
};

const addFileTypeButton = ({ fileName, uid, docType }) => {
    if (DOCUMENT_TYPES_MAP[docType] !== "Internal") {
        return "";
    }

    return getFileTypeButton({
        fileName,
        uid,
    });
};

const formatDate = (value) => {
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
};

const getLinkClasses = (docType, description) => {
    return {
        "supplemental-content-external-link":
            (DOCUMENT_TYPES_MAP[docType] === "Public" ||
                docType === "internal_link") &&
            isBlank(description),
    };
};
</script>

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
            >{{ formatDate(date) }}</span>
            <span
                v-if="!isBlank(name)"
                class="supplemental-content-title"
                :class="getLinkClasses(docType, description)"
            >{{ name }}</span>
            <div
                v-if="!isBlank(description)"
                class="supplemental-content-description"
                :class="getLinkClasses(docType)"
            >
                <span
                    v-sanitize-html="
                        description +
                            addFileTypeButton({
                                fileName,
                                uid,
                                docType,
                            })
                    "
                />
            </div>
        </a>
    </div>
</template>
