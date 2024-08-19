<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import useRemoveList from "composables/removeList";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";

import {
    getCombinedContent,
    getContentWithoutQuery,
    getLastUpdatedDates,
    getInternalSubjects,
    getTitles,
} from "utilities/api";

import { getSubjectName, getSubjectNameParts } from "utilities/filters";

import {
    DOCUMENT_TYPES_MAP,
    getRequestParams,
    PARAM_VALIDATION_DICT,
} from "utilities/utils";

import CategoriesDropdown from "@/components/dropdowns/Categories.vue";
import DocumentTypeSelector from "@/components/subjects/DocumentTypeSelector.vue";
import FetchCategoriesContainer from "@/components/dropdowns/fetchCategoriesContainer.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";
import JumpTo from "@/components/JumpTo.vue";
import PaginationController from "@/components/pagination/PaginationController.vue";
import PolicyResults from "@/components/subjects/PolicyResults.vue";
import PolicySelections from "@/components/subjects/PolicySelections.vue";
import PolicySidebar from "@/components/subjects/PolicySidebar.vue";
import SearchErrorMsg from "@/components/SearchErrorMsg.vue";
import SearchInput from "@/components/SearchInput.vue";
import SelectedSubjectHeading from "@/components/subjects/SelectedSubjectHeading.vue";
import SignInLink from "@/components/SignInLink.vue";
import SubjectSelector from "@/components/subjects/SubjectSelector.vue";
import SubjectTOC from "@/components/subjects/SubjectTOC.vue";

const props = defineProps({
    adminUrl: {
        type: String,
        default: "/admin/",
    },
    aboutUrl: {
        type: String,
        default: "/about/",
    },
    apiUrl: {
        type: String,
        default: "/v3/",
    },
    customLoginUrl: {
        type: String,
        default: "/login",
    },
    hasEditableJobCode: {
        type: Boolean,
        default: false,
    },
    homeUrl: {
        type: String,
        default: "/",
    },
    isAuthenticated: {
        type: Boolean,
        default: false,
    },
    searchUrl: {
        type: String,
        default: "/search/",
    },
    statutesUrl: {
        type: String,
        default: "/statutes/",
    },
    subjectsUrl: {
        type: String,
        default: "/subjects/",
    },
    surveyUrl: {
        type: String,
        default: "",
    },
    username: {
        type: String,
        default: undefined,
    },
});

// Router and Route
const $route = useRoute();
const $router = useRouter();

const FilterTypesDict = {
    subjects: "Subject",
    type: "Type",
    q: "query",
};

const pageSize = 50;

// provide Django template variables
provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);
provide("currentRouteName", $route.name);
provide("customLoginUrl", props.customLoginUrl);
provide("FilterTypesDict", FilterTypesDict);
provide("homeUrl", props.homeUrl);
provide("isAuthenticated", props.isAuthenticated);
</script>

<template>
    <body class="ds-base search-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :apiUrl="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks :statutes-url="statutesUrl" :subjects-url="subjectsUrl" />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
                <template v-if="isAuthenticated" #sign-in>
                    <HeaderUserWidget :admin-url="adminUrl">
                        <template #username>
                            {{ username }}
                        </template>
                    </HeaderUserWidget>
                </template>
                <template v-else #sign-in>
                    <SignInLink
                        :custom-login-url="customLoginUrl"
                        :home-url="homeUrl"
                        :is-authenticated="isAuthenticated"
                        :route="$route"
                    />
                </template>
            </HeaderComponent>
        </header>
    </body>
</template>
