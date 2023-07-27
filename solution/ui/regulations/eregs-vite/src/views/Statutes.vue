<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router/composables";

import { ACT_TYPES } from "eregsComponentLib/src/components/shared-components/Statutes/utils/enums";
import { getStatutes, getStatutesActs } from "utilities/api";
import { shapeTitlesResponse } from "utilities/utils";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";
import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";
import StatuteSelector from "eregsComponentLib/src/components/shared-components/Statutes/StatuteSelector.vue";
import StatuteTable from "eregsComponentLib/src/components/shared-components/Statutes/StatuteTable.vue";
import TableCaption from "eregsComponentLib/src/components/shared-components/Statutes/TableCaption.vue";

import Banner from "@/components/Banner.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import JumpTo from "@/components/JumpTo.vue";

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
});

// get route query params
const $route = useRoute();

// validate query params to make sure they're in the enum?
const queryParams = ref({
    act: $route?.query?.act ?? "ssa",
    title: $route?.query?.title ?? "19",
});

// Act titles -- state, fetch method, parse method
const acts = ref({
    results: [],
    loading: true,
});

const getActTitles = async () => {
    try {
        const actsArray = await getStatutesActs({
            apiUrl: props.apiUrl,
        });

        acts.value.results = actsArray;
    } catch (error) {
        console.error(error);
    } finally {
        acts.value.loading = false;
    }
};

const parsedTitles = computed(() =>
    shapeTitlesResponse({
        actsResults: acts.value.results,
        actTypes: ACT_TYPES,
    })
);

// Statutes -- state and fetch method
const statutes = ref({
    results: [],
    loading: true,
});

const getStatutesArray = async () => {
    statutes.value.loading = true;

    try {
        const statutesArray = await getStatutes({
            act: ACT_TYPES[queryParams.value.act],
            apiUrl: props.apiUrl,
            title: queryParams.value.title,
        });

        statutes.value.results = statutesArray;
    } catch (error) {
        console.error(error);
    } finally {
        statutes.value.loading = false;
    }
};

// watch query params and fetch statutes
watch(
    () => $route.query,
    (newParams, oldParams) => {
        queryParams.value = {
            act: newParams.act,
            title: newParams.title,
        };
    }
);

watch(
    () => queryParams.value,
    async (newParams, oldParams) => {
        await getStatutesArray();
    }
);

// Watch layout
const windowWidth = ref(window.innerWidth);
const isNarrow = computed(() => windowWidth.value < 1024);

// Watch Banner left margin
const bannerRef = ref(null);
const bannerLeftMargin = ref(0);

const getBannerLeftMargin = () => {
    const bannerContent = bannerRef.value.$el
        .getElementsByClassName("content")
        .item(0);

    bannerLeftMargin.value = window.getComputedStyle(bannerContent).marginLeft;
};

const onWidthChange = () => {
    windowWidth.value = window.innerWidth;
    getBannerLeftMargin();
};

onMounted(() => {
    window.addEventListener("resize", onWidthChange);
    getBannerLeftMargin();
});
onUnmounted(() => window.removeEventListener("resize", onWidthChange));

// On load
getActTitles();
getStatutesArray();
</script>

<template>
    <body class="ds-base statute-page">
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
                    />
                </template>
                <template #search>
                    <HeaderSearch :search-url="searchUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="statuteApp" class="statute-view">
            <Banner ref="bannerRef" title="Statute Reference">
                <template #description>
                    <h2>Look up statute text in online sources</h2>
                </template>
            </Banner>
            <div id="main-content" class="statute__container">
                <div class="content" :style="{ marginLeft: bannerLeftMargin }">
                    <div class="content__selector">
                        <div class="selector__parent">
                            <h3>Included Statute</h3>
                            <StatuteSelector
                                v-if="!acts.loading"
                                :loading="statutes.loading"
                                :selected-act="queryParams.act"
                                :selected-title="queryParams.title"
                                :titles="parsedTitles"
                            />
                        </div>
                    </div>
                    <div
                        class="table__parent"
                        :class="{ loading: statutes.loading }"
                    >
                        <SimpleSpinner
                            v-if="statutes.loading"
                            class="table__spinner"
                        />
                        <template v-else>
                            <TableCaption
                                :selected-act="ACT_TYPES[queryParams.act]"
                                :selected-title="queryParams.title"
                            />
                            <StatuteTable
                                :display-type="isNarrow ? 'list' : 'table'"
                                :filtered-statutes="statutes.results"
                                table-type="ssa"
                            />
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </body>
</template>
