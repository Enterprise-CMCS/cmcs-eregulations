<script setup>
import { computed, inject, onMounted, onUnmounted, provide, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { ACT_TYPES } from "eregsComponentLib/src/components/shared-components/Statutes/utils/enums.js";
import { getStatutes, getStatutesActs } from "utilities/api.js";
import { shapeTitlesResponse } from "utilities/utils.js";

import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";
import StatuteSelector from "eregsComponentLib/src/components/shared-components/Statutes/StatuteSelector.vue";
import StatuteTable from "eregsComponentLib/src/components/shared-components/Statutes/StatuteTable.vue";

import AccessLink from "@/components/AccessLink.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import SignInLink from "@/components/SignInLink.vue";
import JumpTo from "@/components/JumpTo.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";

const adminUrl = inject("adminUrl");
const apiUrl = inject("apiUrl");
const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");
const manualUrl = inject("manualUrl");
const searchUrl = inject("searchUrl");
const subjectsUrl = inject("subjectsUrl");
const username = inject("username");

// get route query params
const $route = useRoute();
const $router = useRouter();

provide("router", $router);

const tabRef = ref();

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
            apiUrl,
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
            apiUrl,
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
    (newParams) => {
        queryParams.value = {
            act: newParams.act,
            title: newParams.title,
        };
    }
);

watch(
    () => queryParams.value,
    async () => {
        await getStatutesArray();
    }
);

// Watch layout for narrow table styles
const windowWidth = ref(window.innerWidth);
const isNarrow = computed(() => windowWidth.value < 1024);

const onWidthChange = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => {
    window.addEventListener("resize", onWidthChange);
});
onUnmounted(() => window.removeEventListener("resize", onWidthChange));

// On load
getActTitles();
getStatutesArray();
</script>

<template>
    <body class="ds-base statute-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks
                        :manual-url="manualUrl"
                        :subjects-url="subjectsUrl"
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
                <template v-else #sign-in>
                    <SignInLink
                        :custom-login-url="customLoginUrl"
                        :home-url="homeUrl"
                        :is-authenticated="isAuthenticated"
                        :route="$route"
                    />
                </template>
                <template #get-access>
                    <AccessLink v-if="!isAuthenticated" :base="homeUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="statuteApp" class="statute-view">
            <h1>Look Up Statute Text</h1>
            <h2 class="heading__sans">
                Social Security Act Table of Contents
            </h2>
            <p class="p__description">
                List of sections of
                <a
                    target="_blank"
                    rel="noopener noreferrer"
                    class="external"
                    href="https://uscode.house.gov/view.xhtml?req=granuleid%3AUSC-prelim-title42-chapter7&amp;saved=%7CZ3JhbnVsZWlkOlVTQy1wcmVsaW0tdGl0bGU0Mi1jaGFwdGVyNy1mcm9udA%3D%3D%7C%7C%7C0%7Cfalse%7Cprelim&amp;edition=prelim"
                >42 U.S.C. Chapter 7</a>
                enacted by the Social Security Act.
            </p>
            <div id="main-content" class="statute__container">
                <div class="content">
                    <div class="content__selector">
                        <div class="selector__parent">
                            <StatuteSelector
                                v-if="!acts.loading"
                                v-model:tab-model="tabRef"
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
                            v-if="statutes.loading || acts.loading"
                            class="table__spinner"
                        />
                        <template v-else>
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
