<script setup>
import { computed, inject, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";

import AccessLink from "@/components/AccessLink.vue";
import Banner from "@/components/Banner.vue";
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
const searchUrl = inject("searchUrl");
const subjectsUrl = inject("subjectsUrl");
const username = inject("username");

// get route query params
const $route = useRoute();

// Dummy data for sections with subsections and links
const sections = ref([
    {
        id: 1,
        title: "Part 1 - General",
        subsections: [
            { id: 101, title: "Foreword", web: "https://web.archive.org/web/20010715053550/http://www.hcfa.gov/pubforms/45_smm/foreword.htm", pdf: "https://web.archive.org/web/20041106221936/http://www.cms.hhs.gov/manuals/pub45pdf/smmfwd.pdf" },
        ],
    },
    {
        id: 2,
        title: "Part 2 - State Organization and General Administration",
        subsections: [
            { id: 201, title: "2000. Table of Contents", web: "#web2-1", pdf: "#pdf2-1" },

            { id: 202, title: "2040. Appeals of State Adverse Actions for Medicaid Skilled Nursing and Intermediate Care Facilities (Not Applicable to Federal Terminations of Medicaid Facilities)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2080. Contracts Between State Agencies and Fiscal Agents, Health Care Project Grant Centers, Private Nonmedical Institutions, Health Insuring Organizations, Health Maintenance Organizations, Prepaid Health Plans and for Contracts for Automatic Data Processing Equipment/Services", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2081. Subcontracts", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2082. Specific Requirements for Fiscal Agent Contracts", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2083. Procurement Procedures and Policies for State Medicaid Contracts", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2084 Medicare and Medicaid Health and Safety Standards", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2085. Specific Requirements for Health Maintenance Organizations (HMOs) and Certain Health Insuring Organizations (HIOs)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2086. Eligibility for FFP", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2087. HMO and Certain HIO Contracts - General", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2088. Enrollees and Benefits", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2089. Capitation Payments", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2090. Marketing, Enrollment and Disenrollment", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2091. Quality Assurance", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2092. Additional State Agency Responsibilities", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2100. Free Choice of Providers - General", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2101. Informing Beneficiaries", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2102. Contractual Arrangements", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2103. Exceptions to Freedom of Choice", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2104. Waiver of State Plan Requirements", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2105. Categories of Waivers Under §1915(b)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2106. How to Submit Request for Waiver Under §1915(b)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2107. Documentation Required When Submitting Requests for Waiver Under Section 1915(b)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2108. Documentation of Cost Effectiveness, Access to Care, Quality of Care and Projected Impact of Waiver on the Medicaid Program", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2109. Requests for Modification of an Approved Waiver Program", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2110. Waiver Renewals", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2111. Monitoring, Evaluation, and Termination of Waivers", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2112. Freedom of Choice - Family Planning Services Under §1915(b)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2113. Transportation to Providers of Services", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2114. Case Management for Which No Waiver Is Required", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2200. Requirements for Advance Directives Under State Plans for Medical Assistance", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2350. Legislative Background", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2351. State-PSRO Contracting Process", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2352. Plan Amendment", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2353. Functions Under the State-PSRO Contract", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2354. State Agency Jurisdiction for Hearing and Appeals", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2355. Responsibilities of a State That Does Not Contract With a PSRO", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2356. Transition Issues", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2450. Conflict of Interest Provisions", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2451. Definitions", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2452. Prohibited Activities", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2490. Claiming Federal Financial Participation (FFP) for Advance Payments Made to Providers of Medical Assistance Under Title XIX of the Social Security Actfederal Financial Participation", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2493. Claiming FFP for Provider Payments for State Taxes", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2495. Maintenance of Effort", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2497. Documentation Required to Support a Claim for Federal", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2500. Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2501. Federal Medical Assistance Percentages (FMAP) - State-by-State Tables", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2502. Interest on Disputed Medicaid Claims", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2504 Deeming and Waiver of Nurse Aide Training and Competency Evaluation Requirements", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2505 Nurse Aide Training and Competency Evaluation Programs and Competency Evaluation Programs", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2514. Federal Financial Participation (FFP) for Nurse Aide Training and Competency Evaluation Programs (NATCEPs) and Competency Evaluation Programs (CEPs).", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2515. Federal Financial Participation for Preadmission Screening and Annual Resident Review (PASARR) Activities", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2555. Information on Target Expenditure Levels, Reductions in Medicaid Payments, and Computation of Incentive Rebates to States", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2560. Medicaid Funding Limitations Policy", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2600. Quarterly Budget Estimates - Grants to States for Medical Assistance Program", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2602. Submission Schedule - Medicaid Program Budget Report (Form HCFA-25)", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2700. Federal Reporting Requirements", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2850. Withholding the Federal Share of Payments to Medicaid Providers to Recover Medicare Overpayments; Withholding Medicare Payments to Recover Medicaid Overpayments", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2851. Procedures Required of the Medicaid State Agency to Implement Section 1914", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2852. Procedures Required of the Medicaid State Agency to Implement Section 1885", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2853. Procedures for Refunding the Federal Share of Medicaid Overpayments", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2900. Fair Hearings and Appeals", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2901. Notice and Opportunity for a Fair Hearing", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2902. Hearings", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2903. Hearing Decision", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2904. Reopening and Recovery", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2905. Outstationing of Eligibility Workers General", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2906. Outstation Locations", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2907. Staffing at Outstation Locations", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2908. Guidelines for Outstationing and Providing Application Assistance at Low Use Locations", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2909. Limitations on Outstationed Eligibility Workers", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2910. Application Process", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2911. Applications", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2912. Compliance With Federal Regulations", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2913. FFP for Outstationing", web: "#web2-1", pdf: "#pdf2-1" },
            { id: 202, title: "2975. Contingency Fee Reimbursement for Third Party Liability Identification or Collection", web: "#web2-1", pdf: "#pdf2-1" },
        ],
    },
    {
        id: 3,
        title: "Part 3 - Eligibility",
        web: "#web3",
        pdf: "#pdf3",
        subsections: [
            { id: 301, title: "3200. Changes Due to Welfare Reform", web: "#web3-1", pdf: "#pdf3-1" },
        ],
    },
]);

const expanded = ref({});
const toggleExpand = (id) => {
    expanded.value[id] = !expanded.value[id];
};

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
</script>

<template>
    <div class="ds-base manual-page">
        <header id="header" class="sticky">
            <HeaderComponent :home-url="homeUrl">
                <template #jump-to>
                    <JumpTo :api-url="apiUrl" :home-url="homeUrl" />
                </template>
                <template #links>
                    <HeaderLinks :subjects-url="subjectsUrl" />
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
        <div id="manualApp" class="manual-view">
            <Banner title="State Medicaid Manual" />
            <div id="main-content" class="manual__container">
                <div class="content no-sidebar">
                    <p class="manual-page-description">
                        This page links to copies of the State Medicaid Manual on past versions of the CMS website. 
                        Some sections are not available in past versions. 
                        The complete manual is <a href="https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927">currently available in zip files here</a>.</p>
                    <div class="manual-table-search-row">
                        <form class="search__form" action="#" @submit.prevent>
                            <input type="search" name="q" placeholder="Search within the State Medicaid Manual" />
                            <button type="submit" class="search__button--submit" aria-label="Search">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="9" cy="9" r="7" stroke="#1a355e" stroke-width="2"/>
                                    <line x1="14.2929" y1="14.7071" x2="18" y2="18.4142" stroke="#1a355e" stroke-width="2" stroke-linecap="round"/>
                                </svg>
                            </button>
                        </form>
                    </div>
                    <section class="table__parent">
                        <table id="manualTable">
                            <thead>
                                <tr class="table__row table__row--header">
                                    <th class="table__header">Part/Section</th>
                                    <th class="table__header">Web</th>
                                    <th class="table__header">PDF</th>
                                </tr>
                            </thead>
                            <tbody class="table__body">
                                <template v-for="section in sections" :key="section.id">
                                    <tr class="table__row table__row--body main-row">
                                        <td class="table__cell">
                                            <button class="expand-btn" @click="toggleExpand(section.id)">
                                                <span v-if="section.subsections && section.subsections.length">
                                                    {{ expanded[section.id] ? '▼' : '▶' }}
                                                </span>
                                            </button>
                                            {{ section.title }}
                                        </td>
                                        <td class="table__cell">
                                            
                                        </td>
                                        <td class="table__cell">
                                            
                                        </td>
                                    </tr>
                                    <tr v-if="expanded[section.id] && section.subsections && section.subsections.length"
                                        v-for="sub in section.subsections"
                                        :key="sub.id"
                                        class="table__row table__row--body subsection-row">
                                        <td class="table__cell subsection-cell">
                                            {{ sub.title }}
                                        </td>
                                        <td class="table__cell">
                                            <a :href="sub.web" target="_blank" class="link-btn">Web</a>
                                        </td>
                                        <td class="table__cell">
                                            <a :href="sub.pdf" target="_blank" class="link-btn">PDF</a>
                                        </td>
                                    </tr>
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
.manual-page {
}

.manual__container {
    padding: 0 2rem;
}

.table__parent {
    background: white;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow-x: auto;
    display: flex;
    flex-direction: column;
    justify-content: stretch;
    width: 100%;
}

#manualTable {
    width: 100%;
    border-collapse: collapse;
    height: 100%;
}

.table__header {
    text-align: left;
    padding: 1rem;
    background-color: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
    color: #2c3e50;
}

.table__cell {
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
    color: #2c3e50;
}

.table__row--body.main-row {
    background: #fff;
    font-weight: 600;
}

.table__row--body.subsection-row {
    background: #f8f9fa;
}

.subsection-cell {
    padding-left: 2.5rem;
    font-size: 0.98rem;
    color: #1a355e;
}

.link-btn {
    color: #1976d2;
    text-decoration: underline;
    font-weight: 500;
}

.expand-btn {
    background: none;
    border: none;
    cursor: pointer;
    margin-right: 0.5rem;
    font-size: 1rem;
    color: #1a355e;
}

.sticky {
    position: sticky;
    top: 0;
    z-index: 100;
}

.manual-table-search-row {
    display: flex;
    padding-bottom: 0.5rem;
}
.search__form {
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 3px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    border: 1px solid #e0e6ef;
    padding: 0.25rem 0.5rem;
}
.search__form input[type="search"] {
    flex: 1;
    height: 36px;
    border: none;
    outline: none;
    font-size: 1rem;
    padding: 0 0.5rem;
    background: transparent;
}
.search__button--submit {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0 0.5rem;
    display: flex;
    align-items: center;
}
</style> 