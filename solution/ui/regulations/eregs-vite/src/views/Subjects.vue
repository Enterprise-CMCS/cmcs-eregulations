<script setup>
import { inject, provide, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import useSearchResults from "composables/searchResults.js";
import useRemoveList from "composables/removeList.js";

import isEmpty from "lodash/isEmpty";

import { getLastUpdatedDates, getSubjects, getTitles } from "utilities/api.js";

import { getSubjectName, getSubjectNameParts } from "utilities/filters.js";

import { getRequestParams, PARAM_VALIDATION_DICT } from "utilities/utils.js";

import AccessLink from "@/components/AccessLink.vue";
import CategoriesDropdown from "@/components/dropdowns/Categories.vue";
import DocumentTypeSelector from "@/components/subjects/DocumentTypeSelector.vue";
import FetchItemsContainer from "@/components/dropdowns/FetchItemsContainer.vue";
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
import SubjectSelector from "@/components/subjects/SubjectSelector.vue";
import SubjectLanding from "@/components/subjects/SubjectLanding.vue";

const accessUrl = inject("accessUrl");
const adminUrl = inject("adminUrl");
const apiUrl = inject("apiUrl");
const customLoginUrl = inject("customLoginUrl");
const hasEditableJobCode = inject("hasEditableJobCode");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");
const searchUrl = inject("searchUrl");
const statutesUrl = inject("statutesUrl");
const surveyUrl = inject("surveyUrl");
const username = inject("username");

// Route and router
const $route = useRoute();
const $router = useRouter();

const FilterTypesDict = {
    subjects: "Subject",
    type: "Type",
    q: "query",
};

const pageSize = 50;
const disallowList = ["regulations"];

// provide Django template variables
provide("currentRouteName", $route.name);
provide("FilterTypesDict", FilterTypesDict);

// provide router query params to remove on child component change
const commonRemoveList = ["page", "categories", "intcategories"];
const policySelectionsRemoveList = ["subjects", "q"];
const searchInputRemoveList = commonRemoveList.concat([
    "q",
    "type",
    "categories",
]);

provide("commonRemoveList", commonRemoveList);
provide("policySelectionsRemoveList", policySelectionsRemoveList);

provide("parent", "subjects");

const categoriesRef = ref([]);
const setCategories = (categories) => {
    categoriesRef.value = categories;
};

/**
 * @param {Object} queryParams - $route.query
 * @returns {Boolean} - true if all doc types are selected and nothing else
 */
const allDocTypesOnly = (queryParams) => {
    const { type, ...rest } = queryParams;
    if (
        (type && type.includes("all") && isEmpty(rest)) ||
        (!type && isEmpty(rest))
    ) {
        return true;
    }

    return false;
};

const executeSearch = (payload) => {
    const routeClone = { ...$route.query };

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList: searchInputRemoveList,
    });

    const redirectParams = new URLSearchParams(cleanedRoute);
    const redirectPath = `${homeUrl}search/?${redirectParams.toString() ? redirectParams.toString() + "&" : ""}q=${payload.query}`;
    window.location.assign(redirectPath);
};

// partsLastUpdated fetch for related regulations citations filtering
const partsLastUpdated = ref({
    results: {},
    loading: true,
});

const getPartsLastUpdated = async () => {
    try {
        const titles = await getTitles({ apiUrl });
        partsLastUpdated.value.results = await getLastUpdatedDates({
            apiUrl,
            titles,
        });
    } catch (error) {
        console.error(error);
    } finally {
        partsLastUpdated.value.loading = false;
    }
};

const { policyDocList, getDocList } = useSearchResults();

// use "reactive" method to make urlParams reactive when provided/injected
// selectedParams.paramString is used as the reactive prop
const selectedParams = reactive({
    paramString: "",
    paramsArray: [],
});

// method to add selected params
const addSelectedParams = (paramArgs) => {
    const { id, name, type } = paramArgs;

    // update paramString that is used as reactive prop for watch
    if (selectedParams.paramString) {
        selectedParams.paramString += `&${type}=${id}`;
    } else {
        selectedParams.paramString = `?${type}=${id}`;
    }

    // create new selectedParams key for array of objects for selections
    selectedParams.paramsArray.push({ id, name, type });
};

const clearSelectedParams = () => {
    selectedParams.paramString = "";
    selectedParams.paramsArray = [];
};

const resetSubjects = (linkName) => {
    if (linkName === "subjects") {
        $router.push({
            name: "subjects",
            query: {},
        });
    }
};

provide("selectedParams", selectedParams);

const setSelectedParams = (subjectsListRef) => (param) => {
    const [paramType, paramValue] = param;

    if (commonRemoveList.includes(paramType)) {
        return;
    }

    const paramList = !Array.isArray(paramValue) ? [paramValue] : paramValue;
    paramList.forEach((paramId) => {
        const subject = subjectsListRef.value.results.filter(
            (subjectObj) => paramId === subjectObj.id.toString()
        )[0];

        if (subject) {
            addSelectedParams({
                type: paramType,
                id: paramId,
                name: getSubjectName(subject),
            });
        }
    });
};

// policyDocSubjects fetch for subject selector
// fetch here so we have it in context; pass down to selector via props
const policyDocSubjects = ref({
    results: [],
    loading: true,
});

const setDocumentTitle = (subjectId, subjectList) => {
    const subjectToSelect = subjectList.filter(
        (subjectObj) => subjectObj.id.toString() === subjectId
    )[0];
    const subjName = getSubjectName(subjectToSelect);
    document.title = `${subjName} | ${document.title}`;
};

// called on load
const getDocSubjects = async () => {
    try {
        const subjectsResponse = await getSubjects({
            apiUrl,
        });

        policyDocSubjects.value.results = subjectsResponse.results;
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;

        // set title if needed
        if (policyDocSubjects.value.results.length && $route.query.subjects) {
            setDocumentTitle(
                $route.query.subjects,
                policyDocSubjects.value.results
            );
        }

        // if there's a $route, call addSelectedParams
        if (!allDocTypesOnly($route.query)) {
            // wipe everything clean to start
            clearSelectedParams();

            // now that everything is cleaned, iterate over new query params
            Object.entries($route.query).forEach((param) => {
                setSelectedParams(policyDocSubjects)(param);
            });

            getDocList({
                apiUrl,
                pageSize,
                requestParamString: getRequestParams({
                    queryParams: $route.query,
                    disallowList,
                }),
                query: $route.query.q,
                type: $route.query.type,
            });
        }
    }
};

const selectedSubjectParts = ref([]);

const setSelectedSubjectParts = () => {
    if (selectedParams.paramsArray.length) {
        if (selectedParams.paramsArray[0].id) {
            const selectedSubject = policyDocSubjects.value.results.filter(
                (subjectObj) =>
                    subjectObj.id.toString() ===
                    selectedParams.paramsArray[0].id
            )[0];
            selectedSubjectParts.value = getSubjectNameParts(selectedSubject);
        }
    } else {
        selectedSubjectParts.value = [];
    }
};

const getSearchInputLabel = (selectedSubjectParts) => {
    if (policyDocSubjects.value.loading) {
        return "Loading...";
    }

    if (selectedSubjectParts.length) {
        return `Search within ${selectedSubjectParts[0][0] || selectedSubjectParts[1][0]}`;
    }

    return "Search for a document";
};

watch(
    () => policyDocSubjects.value.loading,
    async (newLoading) => {
        if (!newLoading) {
            setSelectedSubjectParts();
        }
    }
);

watch(
    () => selectedParams.paramString,
    async () => {
        setSelectedSubjectParts();
    }
);

watch(
    () => $route.query,
    async (newQueryParams) => {
        // set title on subject selection
        const { subjects } = newQueryParams;
        if (subjects) {
            const subjectTitleToSet = Array.isArray(subjects)
                ? subjects[0]
                : subjects;
            setDocumentTitle(
                subjectTitleToSet,
                policyDocSubjects.value.results
            );
        }

        // wipe everything clean to start
        clearSelectedParams();

        const sanitizedQueryParams = Object.entries(newQueryParams).filter(
            ([key]) => PARAM_VALIDATION_DICT[key]
        );

        // if all params are removed, return
        if (isEmpty(sanitizedQueryParams)) {
            return;
        }

        // if both internal and external checkboxes are selected and nothing else, return
        if (allDocTypesOnly($route.query)) {
            return;
        }

        // now that everything is cleaned, iterate over new query params
        Object.entries(newQueryParams).forEach(
            setSelectedParams(policyDocSubjects)
        );

        // parse $route.query to return `${key}=${value}` string
        // and provide to getDocList
        const newRequestParams = getRequestParams({
            queryParams: newQueryParams,
            disallowList,
        });
        getDocList({
            apiUrl,
            pageSize,
            requestParamString: newRequestParams,
            query: $route.query.q,
            type: $route.query.type,
        });
    }
);

// fetches on page load
getPartsLastUpdated();
getDocSubjects();
</script>

<template>
    <body class="ds-base subjects-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :statutes-url="statutesUrl"
                        @link-clicked="resetSubjects"
                    />
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
                <template #get-access>
                    <AccessLink v-if="!isAuthenticated" :base="homeUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="subjectsApp" class="repository-view ds-l-container">
            <div class="ds-l-row">
                <div
                    class="ds-l-col--12 ds-l-md-col--4 ds-l-lg-col--3 sidebar__container"
                >
                    <button class="sidebar-toggle__button">
                        Open/Close
                    </button>
                    <PolicySidebar>
                        <template #title>
                            <h2>Research an EO</h2>
                        </template>
                        <template #filters>
                            <SubjectSelector
                                :policy-doc-subjects="policyDocSubjects"
                            >
                                <template #selection="{ selectedSubject }">
                                    <PolicySelections
                                        :selected-subject="selectedSubject"
                                    />
                                </template>
                            </SubjectSelector>
                        </template>
                    </PolicySidebar>
                </div>
                <div class="ds-l-col--12 ds-l-md-col--8 ds-l-lg-col--9">
                    <SubjectLanding
                        v-if="
                            allDocTypesOnly($route.query) ||
                                isEmpty($route.query)
                        "
                        :policy-doc-subjects="policyDocSubjects"
                    />
                    <template v-else>
                        <div
                            v-if="selectedSubjectParts.length"
                            class="subject__heading"
                        >
                            <SelectedSubjectHeading
                                :selected-subject-parts="selectedSubjectParts"
                            />
                        </div>
                        <div class="subject__filters--row">
                            <DocumentTypeSelector v-if="isAuthenticated" />
                            <FetchItemsContainer
                                v-slot="slotProps"
                                items-to-fetch="categories"
                                :items-capture-function="setCategories"
                            >
                                <CategoriesDropdown
                                    :list="slotProps.data"
                                    :error="slotProps.error"
                                    :loading="
                                        slotProps.loading ||
                                            policyDocList.loading
                                    "
                                />
                            </FetchItemsContainer>
                        </div>
                        <div class="subject__search--row">
                            <SearchInput
                                form-class="search-form"
                                :label="
                                    getSearchInputLabel(selectedSubjectParts)
                                "
                                parent="subjects"
                                redirect-to="search"
                                @execute-search="executeSearch"
                            />
                        </div>
                        <template
                            v-if="
                                policyDocList.loading ||
                                    partsLastUpdated.loading
                            "
                        >
                            <span class="loading__span">Loading...</span>
                        </template>
                        <template v-else-if="policyDocList.error">
                            <div class="doc__list">
                                <h2
                                    v-if="!selectedSubjectParts.length"
                                    class="search-results__heading"
                                >
                                    Search Results
                                </h2>
                                <SearchErrorMsg
                                    show-apology
                                    :survey-url="surveyUrl"
                                />
                            </div>
                        </template>
                        <template v-else>
                            <PolicyResults
                                :categories="categoriesRef"
                                :results="policyDocList.results"
                                :results-count="policyDocList.count"
                                :page="parseInt($route.query.page, 10) || 1"
                                :page-size="pageSize"
                                :parts-last-updated="partsLastUpdated.results"
                                :has-editable-job-code="hasEditableJobCode"
                                :selected-subject-parts="selectedSubjectParts"
                            />
                            <div class="pagination-expand-row">
                                <div class="pagination-expand-container">
                                    <PaginationController
                                        v-if="policyDocList.count > 0"
                                        :count="policyDocList.count"
                                        :page="
                                            parseInt($route.query.page, 10) || 1
                                        "
                                        :page-size="pageSize"
                                        view="subjects"
                                    />
                                </div>
                            </div>
                        </template>
                    </template>
                </div>
            </div>
        </div>
    </body>
</template>
