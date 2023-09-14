<script setup>
import { ref } from "vue";
import { getPolicyDocList } from "utilities/api";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";

import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";

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

const getDownloadUrl = (uid) => `${props.apiUrl}file_manager/files/${uid}`;

getDocList();
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
        <div id="policyRepositoryApp" class="repository-view">
            <template v-if="policyDocList.loading">
                <p>Loading...</p>
            </template>
            <template v-else-if="policyDocList.results.length > 0">
                <div
                    v-for="doc in policyDocList.results"
                    :key="doc.uid"
                    class="doc-list__item"
                >
                    <p>Name: {{ doc.name }}</p>
                    <p>Description: {{ doc.description }}</p>
                    <p>UID: {{ doc.uid }}</p>
                    <a :href="getDownloadUrl(doc.uid)">Download</a>
                    <p>Related Citations:</p>
                    <p v-for="loc in doc.locations">
                        {{ loc.title }} CFR § {{ loc.part }}.{{ loc.section_id }}
                    </p>
                </div>
            </template>
            <template v-else>
                <p>No results found.</p>
        </div>
    </body>
</template>
