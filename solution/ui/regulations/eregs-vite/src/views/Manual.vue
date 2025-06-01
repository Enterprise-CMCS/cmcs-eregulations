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
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_01.zip",
        subsections: [
        { id: 101, title: "Foreword", web: "https://web.archive.org/web/20010715053550/http://www.hcfa.gov/pubforms/45_smm/foreword.htm", pdf: "https://web.archive.org/web/20041106221936/http://www.cms.hhs.gov/manuals/pub45pdf/smmfwd.pdf" },
        ],
    },
    {
        id: 2,
        title: "Part 2 - State Organization and General Administration",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_02.zip",
        subsections: [
            { id: 201, title: "2000. Table of Contents", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_toc.htm", pdf: "https://web.archive.org/web/20050204223152/http://www.cms.hhs.gov/manuals/pub45pdf/smm2t.asp" },
            { id: 202, title: "2040. Appeals of State Adverse Actions for Medicaid Skilled Nursing and Intermediate Care Facilities (Not Applicable to Federal Terminations of Medicaid Facilities)", web: "https://web.archive.org/web/20010709053605/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2040_to_2040.htm", pdf: "https://web.archive.org/web/20030630065708/http://www.cms.gov:80/manuals/pub45pdf/2040.pdf" },
            { 
                id: 2080,
                title: "2080 to 2089.9",
                web: "https://web.archive.org/web/20010709053922/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm",
                pdf: "https://web.archive.org/web/20031210081448/http://cms.hhs.gov:80/manuals/pub45pdf/2080.pdf",
                subsections: [
                    { id: 2080, title: "2080. Contracts Between State Agencies and Fiscal Agents, Health Care Project Grant Centers, Private Nonmedical Institutions, Health Insuring Organizations, Health Maintenance Organizations, Prepaid Health Plans and for Contracts for Automatic Data Processing Equipment/Services" },
                    { id: 2081, title: "2081. Subcontracts" },
                    { id: 2082, title: "2082. Specific Requirements for Fiscal Agent Contracts" },
                    { id: 2083, title: "2083. Procurement Procedures and Policies for State Medicaid Contracts" },
                    { id: 2084, title: "2084. Medicare and Medicaid Health and Safety Standards" },
                    { id: 2085, title: "2085. Specific Requirements for Health Maintenance Organizations (HMOs) and Certain Health Insuring Organizations (HIOs)" },
                    { id: 2086, title: "2086. Eligibility for FFP" },
                    { id: 2087, title: "2087. HMO and Certain HIO Contracts - General" },
                    { id: 2088, title: "2088. Enrollees and Benefits" },
                    { id: 2089, title: "2089. Capitation Payments" },
                ]
            },
            { 
                id: 2090,
                title: "2090 to 2092.9",
                web: "https://web.archive.org/web/20010709054313/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2090_to_2092.9.htm",
                pdf: "https://web.archive.org/web/20000929140914/http://www.hcfa.gov:80/pubforms/pub45pdf/20902.pdf",
                subsections: [
                    { id: 2090, title: "2090. Marketing, Enrollment and Disenrollment" },
                    { id: 2091, title: "2091. Quality Assurance" },
                    { id: 2092, title: "2092. Additional State Agency Responsibilities" },
                ]
            },
            { 
                id: 2100,
                title: "2100 to 2106.2",
                web: "https://web.archive.org/web/20010709054643/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2100_to_2106.2.htm",
                pdf: "https://web.archive.org/web/20030910143952/http://cms.gov:80/manuals/pub45pdf/2100.pdf",
                subsections: [
                    { id: 2100, title: "2100. Free Choice of Providers - General" },
                    { id: 2101, title: "2101. Informing Beneficiaries" },
                    { id: 2102, title: "2102. Contractual Arrangements" },
                    { id: 2103, title: "2103. Exceptions to Freedom of Choice" },
                    { id: 2104, title: "2104. Waiver of State Plan Requirements" },
                    { id: 2105, title: "2105. Categories of Waivers Under §1915(b)" },
                    { id: 2106, title: "2106. How to Submit Request for Waiver Under §1915(b)" },
                ]
            },
            { 
                id: 2107,
                title: "2106.3 to 2493",
                web: "https://web.archive.org/web/20010709054557/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2106.3_to_2493.htm",
                pdf: "https://web.archive.org/web/20051208033356/http://www.cms.hhs.gov:80/manuals/pub45pdf/21063.pdf",
                subsections: [
                    { id: 2106, title: "2106. How to Submit Request for Waiver Under §1915(b)" },
                    { id: 2107, title: "2107. Documentation Required When Submitting Requests for Waiver Under Section 1915(b)" },
                    { id: 2108, title: "2108. Documentation of Cost Effectiveness, Access to Care, Quality of Care and Projected Impact of Waiver on the Medicaid Program" },
                    { id: 2109, title: "2109. Requests for Modification of an Approved Waiver Program" },
                    { id: 2110, title: "2110. Waiver Renewals" },
                    { id: 2111, title: "2111. Monitoring, Evaluation, and Termination of Waivers" },
                    { id: 2112, title: "2112. Freedom of Choice - Family Planning Services Under §1915(b)" },
                    { id: 2113, title: "2113. Transportation to Providers of Services" },
                    { id: 2114, title: "2114. Case Management for Which No Waiver Is Required" },
                    { id: 2200, title: "2200. Requirements for Advance Directives Under State Plans for Medical Assistance" },
                    { id: 2350, title: "2350. Legislative Background" },
                    { id: 2351, title: "2351. State-PSRO Contracting Process" },
                    { id: 2352, title: "2352. Plan Amendment" },
                    { id: 2353, title: "2353. Functions Under the State-PSRO Contract" },
                    { id: 2354, title: "2354. State Agency Jurisdiction for Hearing and Appeals" },
                    { id: 2355, title: "2355. Responsibilities of a State That Does Not Contract With a PSRO" },
                    { id: 2356, title: "2356. Transition Issues" },
                    { id: 2450, title: "2450. Conflict of Interest Provisions" },
                    { id: 2451, title: "2451. Definitions" },
                    { id: 2452, title: "2452. Prohibited Activities" },
                    { id: 2490, title: "2490. Claiming Federal Financial Participation (FFP) for Advance Payments Made to Providers of Medical Assistance Under Title XIX of the Social Security Actfederal Financial Participation" },
                    { id: 2493, title: "2493. Claiming FFP for Provider Payments for State Taxes" },
                ]
            },
            { 
                id: 2495,
                title: "2495 to 2500.1",
                web: "https://web.archive.org/web/20010709055045/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2495_to_2500.1.htm",
                pdf: "https://web.archive.org/web/20030910235317/http://cms.gov:80/manuals/pub45pdf/2495.pdf",
                subsections: [
                    { id: 2495, title: "2495. Maintenance of Effort" },
                    { id: 2497, title: "2497. Documentation Required to Support a Claim for Federal" },
                    { id: 2500, title: "2500. Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program" },
                ]
            },
            { id: 2500, title: "2500.2 to 2500.6. Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program",  },
            { 
                id: 2501,
                title: "2501 to 2555",
                web: "https://web.archive.org/web/20010709055542/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2501_to_2555.htm",
                pdf: "https://web.archive.org/web/20030911060906/http://cms.gov:80/manuals/pub45pdf/2501.pdf",
                subsections: [
                    { id: 2501, title: "2501. Federal Medical Assistance Percentages (FMAP) - State-by-State Tables" },
                    { id: 2502, title: "2502. Interest on Disputed Medicaid Claims" },
                    { id: 2504, title: "2504. Deeming and Waiver of Nurse Aide Training and Competency Evaluation Requirements" },
                    { id: 2505, title: "2505. Nurse Aide Training and Competency Evaluation Programs and Competency Evaluation Programs" },
                    { id: 2514, title: "2514. Federal Financial Participation (FFP) for Nurse Aide Training and Competency Evaluation Programs (NATCEPs) and Competency Evaluation Programs (CEPs)." },
                    { id: 2515, title: "2515. Federal Financial Participation for Preadmission Screening and Annual Resident Review (PASARR) Activities" },
                    { id: 2555, title: "2555. Information on Target Expenditure Levels, Reductions in Medicaid Payments, and Computation of Incentive Rebates to States" },
                ]
            },
            { 
                id: 2560,
                title: "2560 to 2600.2",
                web: "https://web.archive.org/web/20010709055530/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2560_to_2600.2.htm",
                pdf: "https://web.archive.org/web/20030911084821/http://cms.gov:80/manuals/pub45pdf/2560.pdf",
                subsections: [
                    { id: 2560, title: "2560. Medicaid Funding Limitations Policy" },
                    { id: 2600, title: "2600. Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                ]
            },
            { id: 2600, title: "2600.3 to 2600.10. Quarterly Budget Estimates - Grants to States for Medical Assistance Program", web: "https://web.archive.org/web/20010709060622/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2600_to_2600.10.htm", pdf: "https://web.archive.org/web/20000929140950/http://www.hcfa.gov:80/pubforms/pub45pdf/26003.pdf" },
            { 
                id: 2600,
                title: "2600.11 to 2602",
                web: "https://web.archive.org/web/20010709060133/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2600.11_to_2602.htm",
                subsections: [
                    { id: 2600, title: "2600. Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                    { id: 2602, title: "2602. Submission Schedule - Medicaid Program Budget Report (Form HCFA-25)" },
                ]
            },
            { id: 2700, title: "2700 to 2700.2. Federal Reporting Requirements", web: "https://web.archive.org/web/20010709061515/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700_to_2700.2.htm", pdf: "https://web.archive.org/web/20030910161000/http://cms.gov:80/manuals/pub45pdf/2700.pdf" },
            { id: 2700, title: "2700.4 to 2700.4. Federal Reporting Requirements", web: "https://web.archive.org/web/20010709060532/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700.4_to_2700.4.htm", pdf: "https://web.archive.org/web/20030910202813/http://cms.gov:80/manuals/pub45pdf/27004.pdf" },
            { id: 2700, title: "2700.6 to 2700.6. Federal Reporting Requirements", web: "https://web.archive.org/web/20010709061449/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700.6_to_2700.6.htm", pdf: "https://web.archive.org/web/20000929141011/http://www.hcfa.gov:80/pubforms/pub45pdf/27006.pdf" },
            { 
                id: 2850,
                title: "2850 to 2853.5",
                web: "https://web.archive.org/web/20010709050741/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2850_to_2853.5.htm",
                pdf: "https://web.archive.org/web/20000929141015/http://www.hcfa.gov:80/pubforms/pub45pdf/2850.pdf",
                subsections: [
                    { id: 2850, title: "2850. Withholding the Federal Share of Payments to Medicaid Providers to Recover Medicare Overpayments; Withholding Medicare Payments to Recover Medicaid Overpayments" },
                    { id: 2851, title: "2851. Procedures Required of the Medicaid State Agency to Implement Section 1914" },
                    { id: 2852, title: "2852. Procedures Required of the Medicaid State Agency to Implement Section 1885" },
                    { id: 2853, title: "2853. Procedures for Refunding the Federal Share of Medicaid Overpayments" },
                ]
            },
            { 
                id: 2900,
                title: "2900.2 to 2975.6",
                web: "https://web.archive.org/web/20010709050940/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2900.2_to_2975.6.htm",
                pdf: "https://web.archive.org/web/20000929141021/http://www.hcfa.gov:80/pubforms/pub45pdf/2900.pdf",
                subsections: [
                    { id: 2900, title: "2900. Fair Hearings and Appeals" },
                    { id: 2901, title: "2901. Notice and Opportunity for a Fair Hearing" },
                    { id: 2902, title: "2902. Hearings" },
                    { id: 2903, title: "2903. Hearing Decision" },
                    { id: 2904, title: "2904. Reopening and Recovery" },
                    { id: 2905, title: "2905. Outstationing of Eligibility Workers General" },
                    { id: 2906, title: "2906. Outstation Locations" },
                    { id: 2907, title: "2907. Staffing at Outstation Locations" },
                    { id: 2908, title: "2908. Guidelines for Outstationing and Providing Application Assistance at Low Use Locations" },
                    { id: 2909, title: "2909. Limitations on Outstationed Eligibility Workers" },
                    { id: 2910, title: "2910. Application Process" },
                    { id: 2911, title: "2911. Applications" },
                    { id: 2912, title: "2912. Compliance With Federal Regulations" },
                    { id: 2913, title: "2913. FFP for Outstationing" },
                    { id: 2975, title: "2975. Contingency Fee Reimbursement for Third Party Liability Identification or Collection" },
                ]
            },
        ],
    },
    {
        id: 3,
        title: "Part 3 - Eligibility",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_03.zip",
        subsections: [
        { id: 300, title: "3000. Table of Contents", web: "https://web.archive.org/web/20010621231541/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_toc.htm", pdf: "https://web.archive.org/web/20040202231037/http://cms.hhs.gov:80/manuals/pub45pdf/smm3t.asp" },
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
                        Most of the manual is outdated, but it may be helpful in some policy areas or for historical reference.
                        This page links to <a 
                            class="external"
                            target="_blank"
                            href="
                            https://web.archive.org/web/20010609052207/http://www.hcfa.gov/pubforms/45_smm/pub45toc.htm
                            ">web</a> 
                        and <a
                            class="external"
                            target="_blank"
                            href="
                            https://web.archive.org/web/20050204151206/http://www.cms.hhs.gov:80/manuals/pub45pdf/smmtoc.asp
                            ">PDF</a>
                        versions from archived copies of the CMS website,
                        along with <a 
                            class="external"
                            target="_blank"
                            href="
                            https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927
                            ">
                            zipped Word documents from the current CMS website</a>.
                        The zip files are the most complete and current version.
                    </p>
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
                                    <th class="table__header">PDF</th>
                                    <th class="table__header">Word</th>
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
                                            <a v-if="section.web" :href="section.web" target="_blank" class="external section-link part-link" @click.prevent="toggleExpand(section.id)">{{ section.title }}</a>
                                            <span v-else class="section-link" @click="toggleExpand(section.id)" style="cursor: pointer;">{{ section.title }}</span>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.pdf" :href="section.pdf" target="_blank" class="link-btn">PDF</a>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.zip" :href="section.zip" target="_blank" class="link-btn">ZIP</a>
                                        </td>
                                    </tr>
                                    <template v-if="expanded[section.id] && section.subsections">
                                        <template v-for="sub in section.subsections" :key="sub.id">
                                            <tr class="table__row table__row--body subsection-row">
                                                <td class="table__cell subsection-cell">
                                                    <button v-if="sub.subsections" class="expand-btn" @click="toggleExpand(sub.id)">
                                                        <span>{{ expanded[sub.id] ? '▼' : '▶' }}</span>
                                                    </button>
                                                    <a v-if="sub.web" :href="sub.web" target="_blank" class="external section-link">{{ sub.title }}</a>
                                                    <span v-else>{{ sub.title }}</span>
                                                </td>
                                                <td class="table__cell">
                                                    <a v-if="sub.pdf" :href="sub.pdf" target="_blank" class="link-btn">PDF</a>
                                                </td>
                                                <td class="table__cell"></td>
                                            </tr>
                                            <template v-if="sub.subsections && expanded[sub.id]">
                                                <tr v-for="nestedSub in sub.subsections" 
                                                    :key="nestedSub.id"
                                                    class="table__row table__row--body nested-subsection-row">
                                                    <td class="table__cell nested-subsection-cell">
                                                        <a v-if="nestedSub.web" :href="nestedSub.web" target="_blank" class="external section-link">{{ nestedSub.title }}</a>
                                                        <span v-else>{{ nestedSub.title }}</span>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a v-if="nestedSub.pdf" :href="nestedSub.pdf" target="_blank" class="link-btn">PDF</a>
                                                    </td>
                                                    <td class="table__cell"></td>
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

.nested-subsection-cell {
    padding-left: 4rem;
    font-size: 0.95rem;
}

.nested-subsection-row {
    background: #f0f2f5;
}

.section-link {
    text-decoration: none;
}

.part-link {
    text-decoration: none;
    cursor: pointer;
}


</style> 