<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";

import { getStatutes } from "utilities/api";

import BlockingModal from "eregsComponentLib/src/components/BlockingModal.vue";
import FlashBanner from "eregsComponentLib/src/components/FlashBanner.vue";
import IFrameContainer from "eregsComponentLib/src/components/IFrameContainer.vue";
import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";
import StatuteTable from "eregsComponentLib/src/components/shared-components/Statutes/StatuteTable.vue";

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

// Get statutes
const statutes = ref({
    results: [],
    loading: true,
});
const getStatutesArray = async () => {
    try {
        const statutesArray = await getStatutes({ apiUrl: props.apiUrl });
        statutes.value.results = statutesArray;
    } catch (error) {
        console.error(error);
    } finally {
        statutes.value.loading = false;
    }
};

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
                    <div class="table__parent">
                        <SimpleSpinner
                            v-if="statutes.loading"
                            class="table__spinner"
                        />
                        <template v-else>
                            <div class="table__caption">
                                In selected Social Security Act titles (XI, XVI,
                                XVIII, XIX, XXI), find equivalent US Code
                                citations and read the text in your choice of
                                government website. Coming up soon: more
                                navigation options and additional statutes.<br />
                                Learn more about these sources:
                                <a
                                    class="external"
                                    href="https://uscode.house.gov/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    >US Code House.gov</a
                                >,
                                <a
                                    class="external"
                                    href="https://www.govinfo.gov/app/collection/comps/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    >Statute Compilation</a
                                >,
                                <a
                                    class="external"
                                    href="https://www.govinfo.gov/app/collection/uscode"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    >US Code Annual</a
                                >,
                                <a
                                    class="external"
                                    href="https://www.ssa.gov/OP_Home/ssact/ssact.htm"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    >SSA.gov Compilation</a
                                >.
                            </div>
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

<style></style>
