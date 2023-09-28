<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router/composables";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";

import Banner from "@/components/Banner.vue";
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

const executeSearch = (payload) => {
    console.log("executeSearch", payload);
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
        query: {
            q: undefined,
        },
    });
};
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
        </div>
    </body>
</template>

<style></style>
