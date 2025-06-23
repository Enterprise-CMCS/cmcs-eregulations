<script setup>
import { DOCUMENT_TYPES_MAP, getFileTypeButton, getLinkDomainFileTypeEl, getLinkDomainString } from "utilities/utils";
import { ref } from "vue";
import SubjectChips from "../../../eregs-vite/src/components/subjects/SubjectChips.vue";

defineProps({
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
    subjects: {
        type: Array,
        required: false,
        default: undefined,
    },
});

const isBlank = (str) => {
    return !str || /^\s*$/.test(str);
};

const addFileTypeButton = ({ fileName, uid, url, docType }) => {
    if (docType == "public_link" || docType == "internal_link") {
        return getFileTypeButton({
            fileName: url,
            uid: uid ?? url,
        });
    }

    if (DOCUMENT_TYPES_MAP[docType] == "Internal") {
        return getFileTypeButton({
            fileName,
            uid,
        });
    }

    return "";
};

const addDomainFileTypeEl = ({ title, fileName, uid, url, docType }) => {
    const domainString = getLinkDomainString({url, className: "supplemental-content-domain"});
    const fileTypeButton = addFileTypeButton({
        fileName,
        uid,
        url,
        docType,
    })
    return getLinkDomainFileTypeEl(title, domainString, fileTypeButton);
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
                docType === "internal_link") && isBlank(description),
    };
};

const showSubjects = ref(false);
const hasSubjects = (subjects) => Array.isArray(subjects) && subjects.length > 0;
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
                    v-sanitize-html="addDomainFileTypeEl({ title: description, fileName, uid, url, docType })"
                />
            </div>
        </a>
        <div v-if="hasSubjects(subjects)" class="supplemental-content-subjects">
            <a
                href="#"
                class="supplemental-content-subjects-toggle"
                @click.prevent="showSubjects = !showSubjects"
            >
                <span v-if="!showSubjects">
                    Show Related Subjects
                    <i class="fa fa-chevron-down" />
                </span>
                <span v-else>
                    Hide Related Subjects
                    <i class="fa fa-chevron-up" />
                </span>
            </a>
            <div v-if="showSubjects" class="supplemental-content-subjectchips">
                <SubjectChips :subjects="subjects" />
            </div>
        </div>
    </div>
</template>
