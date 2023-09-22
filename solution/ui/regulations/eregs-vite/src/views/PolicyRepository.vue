<script setup>
import { provide, reactive, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import {
    getLastUpdatedDates,
    getPolicyDocList,
    getTitles,
} from "utilities/api";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import PolicyResults from "@/components/policy-repository/PolicyResults.vue";
import PolicySelections from "@/components/policy-repository/PolicySelections.vue";
import PolicySidebar from "@/components/policy-repository/PolicySidebar.vue";
import SubjectSelector from "@/components/policy-repository/SubjectSelector.vue";

const props = defineProps({
    aboutUrl: {
        type: String,
        default: "/about/",
    },
    apiUrl: {
        type: String,
        default: "/v3/",
    },
    homeUrl: {
        type: String,
        default: "/",
    },
    resourcesUrl: {
        type: String,
        default: "/resources/",
    },
    searchUrl: {
        type: String,
        default: "/search/",
    },
    statutesUrl: {
        type: String,
        default: "/statutes/",
    },
    isAuthenticated: {
        type: Boolean,
        default: false,
    },
});

provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);

const partsLastUpdated = ref({
    results: {},
    loading: true,
});

const getPartsLastUpdated = async () => {
    try {
        const titles = await getTitles();
        partsLastUpdated.value.results = await getLastUpdatedDates(
            props.apiUrl,
            titles
        );
    } catch (error) {
        console.error(error);
    } finally {
        partsLastUpdated.value.loading = false;
    }
};

const policyDocList = ref({
    results: [],
    loading: true,
});

const getDocList = async (requestParams = "") => {
    try {
        policyDocList.value.results = await getPolicyDocList({
            apiUrl: props.apiUrl,
            cacheResponse: !props.isAuthenticated,
            requestParams,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocList.value.loading = false;
    }
};

// Router and Route
const $router = useRouter();
const $route = useRoute();

// use reactive to make urlParams reactive when provided/injected
const selectedParamsObj = reactive({ paramString: "", params: {} });

provide("selectedParams", {
    selectedParamsObj,
    updateSelectedParams: (paramArgs) => {
        const { action, id, name, type } = paramArgs;

        // early return if removing a selected param
        if (action === "remove") {
            // early return if removing a param that is not selected
            if (!selectedParamsObj.params[type]) return;

            // remove from selectedParamsObj.paramString
             const stringToEdit = selectedParamsObj.paramString
                .substring(1)
                .split("&")
                .filter((param) => param !== `${type}=${id}`)
                .join("&");

            selectedParamsObj.paramString = `?${stringToEdit}`;

            // remove from selectedParamsObj.params
            selectedParamsObj.params[type] = selectedParamsObj.params[type]
                .split(",")
                .filter((param) => param !== id)
                .join(",");

            // remove from selectedParamsObj.params if empty
            if (!selectedParamsObj.params[type]) {
                delete selectedParamsObj.params[type];
            }

            return;
        }

        // early return if the param is already selected
        if (
            action === "add" &&
            selectedParamsObj.paramString.includes(`${type}=${id}`)
        )
            return;

        // update paramString that is used as reactive prop for watch
        if (selectedParamsObj.paramString) {
            selectedParamsObj.paramString += `&${type}=${id}`;
        } else {
            selectedParamsObj.paramString = `?${type}=${id}`;
        }

        // update paramsObj that is used to update the url
        if (selectedParamsObj.params[type]) {
            selectedParamsObj.params[type] += `,${id}`;
        } else {
            selectedParamsObj.params[type] = `${id}`;
        }
    },
});

// watch for changes to selectedParamsObj.paramString and update url
watch(
    () => selectedParamsObj.paramString,
    async () => {
        $router.push({
            name: "policy-repository",
            query: { ...selectedParamsObj.params },
        });
    }
);

// watch for changes to url and fetch new results
watch(
    () => $route.query,
    async (newParams) => {
        // parse $route.query to return `${key}=${value}` string
        const requestParams = Object.entries(newParams)
            .map(([key, value]) => {
                const valueArray = value.split(",");
                return valueArray.map((v) => `${key}=${v}`).join("&");
            })
            .join("&");

        await getDocList(requestParams);
    }
);

getDocList();
getPartsLastUpdated();
</script>

<template>
    <body class="ds-base policy-repository-page">
        <BlockingModal>
            <IFrameContainer
                src="https://docs.google.com/forms/d/e/1FAIpQLSdcG9mfTz6Kebdni8YSacl27rIwpGy2a7GsMGO0kb_T7FSNxg/viewform?embedded=true"
                title="Google Forms iframe"
            />
        </BlockingModal>
        <FlashBanner />
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :about-url="aboutUrl"
                        :resources-url="resourcesUrl"
                        :statutes-url="statutesUrl"
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="policyRepositoryApp" class="repository-view ds-l-container">
            <div class="ds-l-row">
                <div
                    class="ds-l-col--12 ds-l-md-col--4 ds-l-lg-col--3 sidebar__container"
                >
                    <PolicySidebar>
                        <template #title>
                            <h2>Find Policy Documents</h2>
                        </template>
                        <template #selections>
                            <PolicySelections />
                        </template>
                        <template #filters>
                            <SubjectSelector />
                        </template>
                    </PolicySidebar>
                </div>
                <div class="ds-l-col--12 ds-l-md-col--8 ds-l-lg-col--9">
                    <template
                        v-if="policyDocList.loading || partsLastUpdated.loading"
                    >
                        <p>Loading...</p>
                    </template>
                    <template v-else>
                        <PolicyResults
                            :base="homeUrl"
                            :results="policyDocList.results"
                            :parts-last-updated="partsLastUpdated.results"
                        />
                    </template>
                </div>
            </div>
        </div>
    </body>
</template>
