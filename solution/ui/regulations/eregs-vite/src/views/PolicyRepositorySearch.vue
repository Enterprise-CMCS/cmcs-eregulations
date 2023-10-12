<script setup>
import { provide, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router/composables";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";

import {
    getLastUpdatedDates,
    getPolicyDocList,
    getTitles,
} from "utilities/api";

import { getRequestParams } from "utilities/utils";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";

import Banner from "@/components/Banner.vue";
import PolicyResults from "@/components/policy-repository/PolicyResults.vue";
import SearchInput from "@/components/SearchInput.vue";

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

// Router and Route
const $route = useRoute();
const $router = useRouter();

// provide Django template variables
provide("apiUrl", props.apiUrl);
provide("base", props.homeUrl);

// partsLastUpdated fetch for related regulations citations filtering
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

const searchQuery = ref($route.query.q ?? "");

// policyDocList fetch for policy document list
const policyDocList = ref({
    loading: false,
    results: [],
});

const getDocList = async (requestParams = "") => {
    policyDocList.value.loading = true;

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

const executeSearch = (payload) => {
    $router.push({
        name: "policy-repository-search",
        query: {
            q: payload.query,
        },
    });
};

const clearSearchQuery = () => {
    $router.push({
        name: "policy-repository-search",
        query: {},
    });
};

watch(
    () => $route.query,
    async (newQueryParams, oldQueryParams) => {
        if (_isEmpty(newQueryParams)) {
            searchQuery.value = "";
            return;
        }

        searchQuery.value = newQueryParams.q ?? "";
    }
);

watch(searchQuery, async (newSearchQuery, oldSearchQuery) => {
    if (newSearchQuery === oldSearchQuery) {
        return;
    }

    if (_isEmpty(newSearchQuery)) {
        policyDocList.value.results = [];
        return;
    }

    getDocList(getRequestParams($route.query));
});

getPartsLastUpdated();

// searchQuery is populated on load from $route.query.q, fetch docs list
if (!_isEmpty(searchQuery.value)) {
    getDocList(getRequestParams($route.query));
}
</script>

<template>
    <body class="ds-base policy-repository-search-page">
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
        <div id="policyRepositorySearchApp" class="repository-search-view">
            <Banner title="Search Results">
                <template #input>
                    <SearchInput
                        form-class="search-form"
                        label="Search Unpublished Documents"
                        page="policy-repository-search"
                        :search-query="searchQuery"
                        @execute-search="executeSearch"
                        @clear-form="clearSearchQuery"
                    />
                </template>
            </Banner>
            <div class="results__container ds-l-container">
                <div class="ds-l-row">
                    <div
                        class="ds-l-col--10 ds-u-margin-left--auto ds-u-margin-right--auto"
                    >
                        <template v-if="policyDocList.loading">
                            <span class="loading__span">Loading...</span>
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
        </div>
    </body>
</template>
