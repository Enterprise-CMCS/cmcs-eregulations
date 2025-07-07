<script setup>
import { useId } from "vue";
import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";
import SubjectChips from "spaComponents/subjects/SubjectChips.vue";

import { DOCUMENT_TYPES_MAP, getFileTypeButton, getLinkDomainFileTypeEl, getLinkDomainString } from "utilities/utils";

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

const uid = useId();

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
        <template v-if="hasSubjects(subjects)">
            <CollapseButton
                class="supplemental-content-subjects"
                :name="'subjects-' + uid"
                state="collapsed"
            >
                <template #expanded>
                    Hide Related Subjects
                    <i class="fa fa-chevron-up" />
                </template>
                <template #collapsed>
                    Show Related Subjects
                    <i class="fa fa-chevron-down" />
                </template>
            </CollapseButton>
            <Collapsible
                :name="'subjects-' + uid"
                state="collapsed"
                class="collapse-content"
                overflow
            >
                <SubjectChips
                    :subjects="subjects"
                />
            </Collapsible>
        </template>
    </div>
</template>
