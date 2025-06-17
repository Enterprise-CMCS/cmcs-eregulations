<script setup>
import { inject, ref } from "vue";
import { useRoute } from "vue-router";

import AccessLink from "@/components/AccessLink.vue";
import Banner from "@/components/Banner.vue";
import FetchItemsContainer from "@/components/dropdowns/FetchItemsContainer.vue";
import HeaderComponent from "@/components/header/HeaderComponent.vue";
import HeaderLinks from "@/components/header/HeaderLinks.vue";
import HeaderSearch from "@/components/header/HeaderSearch.vue";
import SearchInput from "@/components/SearchInput.vue";
import SignInCTA from "@/components/SignInCTA.vue";
import SignInLink from "@/components/SignInLink.vue";
import JumpTo from "@/components/JumpTo.vue";
import HeaderUserWidget from "@/components/header/HeaderUserWidget.vue";

import smmTableData from "@/components/manual/data/smm-table-data.js";

const accessUrl = inject("accessUrl");
const adminUrl = inject("adminUrl");
const apiUrl = inject("apiUrl");
const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");
const searchUrl = inject("searchUrl");
const statutesUrl = inject("statutesUrl");
const subjectsUrl = inject("subjectsUrl");
const username = inject("username");

const $route = useRoute();

const expanded = ref({});
const toggleExpand = (id) => {
    expanded.value[id] = !expanded.value[id];
};

const smmCatIdRef = ref(null);
const setSmmCatId = (categories) => {
    if (!categories.loading || !categories.error) {
        const smmCategory = categories.find(cat => cat.is_smm_category);
        smmCatIdRef.value = smmCategory ? smmCategory.id : null;
    } else {
        smmCatIdRef.value = null;
    }
};

const getSearchInputLabel = (fetchCategoriesProps) => {
    if (fetchCategoriesProps.loading) {
        return "Loading...";
    }

    if (smmCatIdRef.value) {
        return "Search within the manual";
    }

    return "Search";
};

const executeSearch = (payload) => {
    const catId = smmCatIdRef.value ? `type=internal&intcategories=${smmCatIdRef.value}&` : "";
    const redirectPath = `${homeUrl}search/?${catId}q=${payload.query}`;
    window.location.assign(redirectPath);
};

</script>

<template>
    <div class="ds-base manual-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
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
                <template #get-access>
                    <AccessLink v-if="!isAuthenticated" :base="homeUrl" />
                </template>
            </HeaderComponent>
        </header>
        <div id="manualApp" class="site-container">
            <Banner title="State Medicaid Manual" />
            <div id="main-content" class="manual__container">
                <div class="">
                    <p class="manual-page-description">
                        This table provides links to
                        <a
                            class="external"
                            target="_blank"
                            rel="noopener noreferrer"
                            href="https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927"
                        >
                            zipped Word documents from the CMS website</a>,
                        which is the most current and complete version of the manual,
                        along with links to convenient
                        <a
                            class="external"
                            target="_blank"
                            rel="noopener noreferrer"
                            href="https://web.archive.org/web/20041212094406/http://www.cms.hhs.gov/manuals/45_smm/pub45toc.asp"
                        >
                            web pages</a>
                        and
                        <a
                            class="external"
                            target="_blank"
                            rel="noopener noreferrer"
                            href="https://web.archive.org/web/20050204151206/http://www.cms.hhs.gov:80/manuals/pub45pdf/smmtoc.asp"
                        >
                            PDFs</a>
                        from archived copies of the CMS website.
                    </p>
                    <section class="search__container">
                        <div v-if="isAuthenticated" class="search-input__div">
                            <FetchItemsContainer
                                v-slot="slotProps"
                                items-to-fetch="categories"
                                :items-capture-function="setSmmCatId"
                            >
                                <SearchInput
                                    form-class="search-form"
                                    :label="getSearchInputLabel(slotProps)"
                                    :disabled="slotProps.loading"
                                    parent="manual"
                                    redirect-to="search"
                                    @execute-search="executeSearch"
                                />
                            </FetchItemsContainer>
                        </div>
                        <SignInCTA
                            v-else
                            class="login-cta__div--manual"
                            :access-url="accessUrl"
                            desired-action-string="search within the manual"
                            :is-authenticated="isAuthenticated"
                            test-id="loginManual"
                        >
                            <template #sign-in-link>
                                <SignInLink
                                    :custom-login-url="customLoginUrl"
                                    :home-url="homeUrl"
                                    :is-authenticated="isAuthenticated"
                                    :route="$route"
                                />
                            </template>
                        </SignInCTA>
                    </section>
                    <section class="table__parent">
                        <table id="manualTable">
                            <thead>
                                <tr class="table__row table__row--header">
                                    <th class="table__header">
                                        <div class="cell__title">
                                            Part/Section
                                        </div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">
                                            Word (ZIP)
                                        </div>
                                        <div class="cell__subtitle">
                                            Current
                                        </div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">
                                            Web
                                        </div>
                                        <div class="cell__subtitle">
                                            Archived
                                        </div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">
                                            PDF
                                        </div>
                                        <div class="cell__subtitle">
                                            Archived
                                        </div>
                                    </th>
                                </tr>
                            </thead>
                            <tbody class="table__body">
                                <template v-for="section in smmTableData" :key="section.id">
                                    <tr class="table__row table__row--body main-row">
                                        <td class="table__cell">
                                            <button
                                                class="expand-btn"
                                                @click="toggleExpand(section.id)"
                                            >
                                                <span v-if="section.subsections && section.subsections.length">
                                                    <i :class="['fa', expanded[section.id] ? 'fa-angle-down' : 'fa-angle-right']" />
                                                </span>
                                            </button>
                                            <span
                                                v-if="section.id || section.title"
                                                :class="['section-text', { 'section-link': section.subsections }]"
                                                @click="section.subsections && toggleExpand(section.id)"
                                            >
                                                <span>{{ section.title }}</span>
                                            </span>
                                        </td>
                                        <td class="table__cell">
                                            <a
                                                v-if="section.doc?.url"
                                                :href="section.doc.url"
                                                target="_blank"
                                                class="link-btn"
                                                rel="noopener noreferrer"
                                            >
                                                Word
                                                <span v-if="section.doc.date" class="date-stamp">
                                                    ({{ section.doc.date }})
                                                </span>
                                            </a>
                                        </td>
                                        <td class="table__cell">
                                            <a
                                                v-if="section.web?.url"
                                                :href="section.web.url"
                                                target="_blank"
                                                class="link-btn"
                                                rel="noopener noreferrer"
                                            >
                                                Web
                                                <span v-if="section.web.date" class="date-stamp">
                                                    ({{ section.web.date }})
                                                </span>
                                            </a>
                                        </td>
                                        <td class="table__cell">
                                            <a
                                                v-if="section.pdf?.url"
                                                :href="section.pdf.url"
                                                target="_blank"
                                                class="link-btn"
                                                rel="noopener noreferrer"
                                            >
                                                PDF
                                                <span v-if="section.pdf.date" class="date-stamp">
                                                    ({{ section.pdf.date }})
                                                </span>
                                            </a>
                                            <span v-else-if="section.pdf?.date" class="date-stamp">
                                                ({{ section.pdf.date }})
                                            </span>
                                        </td>
                                    </tr>
                                    <template v-if="expanded[section.id] && section.subsections">
                                        <template v-for="sub in section.subsections" :key="sub.id">
                                            <tr class="table__row table__row--body subsection-row">
                                                <td class="table__cell subsection-cell">
                                                    <button
                                                        v-if="sub.subsections"
                                                        class="expand-btn"
                                                        @click="toggleExpand(sub.id)"
                                                    >
                                                        <i :class="['fa', expanded[sub.id] ? 'fa-angle-down' : 'fa-angle-right']" />
                                                    </button>
                                                    <span
                                                        v-if="sub.id || sub.title"
                                                        :class="['section-text', { 'section-link': sub.subsections }]"
                                                        @click="sub.subsections && toggleExpand(sub.id)"
                                                    >
                                                        <span v-if="sub.id" class="section-number">
                                                            {{ sub.id }}{{ sub.title ? '. ' : '' }}
                                                        </span>
                                                        <span>{{ sub.title }}</span>
                                                    </span>
                                                </td>
                                                <td class="table__cell">
                                                    <a
                                                        v-if="sub.doc?.url"
                                                        :href="sub.doc.url"
                                                        target="_blank"
                                                        class="link-btn"
                                                        rel="noopener noreferrer"
                                                    >
                                                        Word
                                                        <span v-if="sub.doc.date" class="date-stamp">
                                                            ({{ sub.doc.date }})
                                                        </span>
                                                    </a>
                                                    <span v-else-if="sub.doc?.date" class="date-stamp">
                                                        ({{ sub.doc.date }})
                                                    </span>
                                                </td>
                                                <td class="table__cell">
                                                    <a
                                                        v-if="sub.web?.url"
                                                        :href="sub.web.url"
                                                        target="_blank"
                                                        class="link-btn"
                                                        rel="noopener noreferrer"
                                                    >
                                                        Web
                                                        <span v-if="sub.web.date" class="date-stamp">
                                                            ({{ sub.web.date }})
                                                        </span>
                                                    </a>
                                                    <span v-else-if="sub.web?.date" class="date-stamp">
                                                        ({{ sub.web.date }})
                                                    </span>
                                                </td>
                                                <td class="table__cell">
                                                    <a
                                                        v-if="sub.pdf?.url"
                                                        :href="sub.pdf.url"
                                                        target="_blank"
                                                        class="link-btn"
                                                        rel="noopener noreferrer"
                                                    >
                                                        PDF
                                                        <span v-if="sub.pdf.date" class="date-stamp">
                                                            ({{ sub.pdf.date }})
                                                        </span>
                                                    </a>
                                                    <span v-else-if="sub.pdf?.date" class="date-stamp">
                                                        ({{ sub.pdf.date }})
                                                    </span>
                                                </td>
                                            </tr>
                                            <template v-if="sub.subsections && expanded[sub.id]">
                                                <tr
                                                    v-for="nestedSub in sub.subsections"
                                                    :key="nestedSub.id"
                                                    class="table__row table__row--body nested-subsection-row"
                                                >
                                                    <td class="table__cell nested-subsection-cell">
                                                        <span
                                                            v-if="nestedSub.id || nestedSub.title"
                                                            :class="['section-text', { 'section-link': nestedSub.subsections }]"
                                                            @click="nestedSub.subsections && toggleExpand(nestedSub.id)"
                                                        >
                                                            <span v-if="nestedSub.id" class="section-number">
                                                                {{ nestedSub.id }}{{ nestedSub.title ? '. ' : '' }}
                                                            </span>
                                                            <span>{{ nestedSub.title }}</span>
                                                        </span>
                                                    </td>
                                                    <td class="table__cell">
                                                        <span v-if="nestedSub.doc?.date" class="date-stamp">
                                                            ({{ nestedSub.doc.date }})
                                                        </span>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a
                                                            v-if="nestedSub.web?.url"
                                                            :href="nestedSub.web.url"
                                                            target="_blank"
                                                            class="link-btn"
                                                            rel="noopener noreferrer"
                                                        >
                                                            Web
                                                            <span v-if="nestedSub.web.date" class="date-stamp">
                                                                ({{ nestedSub.web.date }})
                                                            </span>
                                                        </a>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a
                                                            v-if="nestedSub.pdf?.url"
                                                            :href="nestedSub.pdf.url"
                                                            target="_blank"
                                                            class="link-btn"
                                                            rel="noopener noreferrer"
                                                        >
                                                            PDF
                                                            <span v-if="nestedSub.pdf.date" class="date-stamp">
                                                                ({{ nestedSub.pdf.date }})
                                                            </span>
                                                        </a>
                                                        <span v-else-if="nestedSub.pdf?.date" class="date-stamp">
                                                            ({{ nestedSub.pdf.date }})
                                                        </span>
                                                    </td>
                                                </tr>
                                            </template>
                                        </template>
                                    </template>
                                </template>
                            </tbody>
                        </table>
                    </section>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.manual__container {
    padding: 0 2rem;
}

.search__container {
    margin-bottom: 1rem;
}

.search__container .search-input__div {
    width: 320px;
}

.table__parent {
    border-radius: 4px;
    overflow-x: auto;
    width: 100%;
}

#manualTable {
    width: 100%;
    border-collapse: collapse;
}

.table__header {
    text-align: left;
    vertical-align: top;
    padding: 0.5rem 0 0.5rem 1.5rem;
    background-color: #254c68;
    border-bottom: 2px solid #dee2e6;
    font-weight: 700;
    color: #fff;
}

/* Fixed widths for document type columns */
.table__header:nth-child(2),
.table__header:nth-child(3),
.table__header:nth-child(4) {
    width: 130px;
    padding: 0.5rem 0 0.5rem 1rem;
}

.cell__subtitle {
    font-weight: normal;
    font-style: italic;
    font-size: 14px;
}

.table__cell {
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
    vertical-align: top;
}

/* Fixed widths for document type columns */
.table__cell:nth-child(2),
.table__cell:nth-child(3),
.table__cell:nth-child(4) {
    width: 130px;
}

.table__row--body.main-row {
    background: #f0f2f5;
    font-weight: 600;
}

.table__row--body.subsection-row {
    background: #f8f9fa;
}

.table__row--body.nested-subsection-row {
    background: #fff;
}

.subsection-cell {
    padding-left: 3rem;
    font-size: 0.98rem;
}

.subsection-cell .expand-btn {
    margin-left: -1rem;
}

.nested-subsection-cell {
    padding-left: 4rem;
    font-size: 0.95rem;
}

.link-btn {
    color: #1976d2;
    font-weight: 500;
    text-decoration: none;
}

.expand-btn {
    background: none;
    border: none;
    cursor: pointer;
    margin-right: 0.5rem;
    font-size: 1rem;
    color: #1a355e;
}

.fa-angle-right {
    margin-right: 2px; /* adjust for the right-arrow and down-arrow being slightly different sizes */
}

.section-text {
    text-decoration: none;
}

.section-link {
    cursor: pointer;
}

.section-number {
    font-weight: 600;
}

.date-stamp {
    font-size: 0.8em;
    color: #5b616b;
    margin-left: 4px;
    font-weight: 500;
}
</style>
