<script setup>
import { provide, reactive, ref } from "vue";
import { useRoute } from "vue-router/composables";

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

// get route query params
const $route = useRoute();

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

const getDocList = async () => {
    try {
        policyDocList.value.results = await getPolicyDocList({
            apiUrl: props.apiUrl,
            cacheResponse: !props.isAuthenticated,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocList.value.loading = false;
    }
};

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
                <div class="ds-l-col--12 ds-l-md-col--4 ds-l-lg-col--3 sidebar__container">
                    <PolicySidebar>
                        <template #title>
                            <h2>Find Policy Documents</h2>
                        </template>
                        <template #filters>
                            <SubjectSelector />
                        </template>
                    <PolicySidebar />
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
