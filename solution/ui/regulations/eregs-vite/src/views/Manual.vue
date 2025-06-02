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

const $route = useRoute();

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
            { id: 2000, title: "2000. Table of Contents", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_toc.htm", pdf: "https://web.archive.org/web/20050204223152/http://www.cms.hhs.gov/manuals/pub45pdf/smm2t.asp" },
            { id: 2040, title: "2040. Appeals of State Adverse Actions for Medicaid Skilled Nursing and Intermediate Care Facilities (Not Applicable to Federal Terminations of Medicaid Facilities)", web: "https://web.archive.org/web/20010709053605/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2040_to_2040.htm", pdf: "https://web.archive.org/web/20030630065708/http://www.cms.gov:80/manuals/pub45pdf/2040.pdf" },
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
        { id: 3000, title: "3000. Table of Contents", web: "https://web.archive.org/web/20010621231541/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_toc.htm", pdf: "https://web.archive.org/web/20040202231037/http://cms.hhs.gov:80/manuals/pub45pdf/smm3t.asp" },
        { 
            id: 3200,
            title: "3200 to 3207",
            web: "https://web.archive.org/web/20010715053855/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3200_to_3207.htm",
            pdf: "https://web.archive.org/web/20000929141030/http://www.hcfa.gov:80/pubforms/pub45pdf/sm3200.pdf",
            subsections: [
                { title: "3200 Changes Due to Welfare Reform", web: "", pdf: "" },
                { title: "3207 Changes in SSI Definition of Disability Due to Welfare Reform", web: "", pdf: "" },
            ]
        },
        { 
            id: 3210,
            title: "3210 to 3256",
            web: "https://web.archive.org/web/20010715054127/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3210_to_3256.htm",
            pdf: "https://web.archive.org/web/20030808034231/http://www.cms.hhs.gov/manuals/pub45pdf/sm3210.pdf",
            subsections: [
                { title: "3210 Citizenship and Alienage", web: "", pdf: "" },
                { title: "3211 Aliens", web: "", pdf: "" },
                { title: "3212 Documentation and Verification of Status as Citizen or Alien", web: "", pdf: "" },
                { title: "3213 Redeterminations and FFP Availability", web: "", pdf: "" },
                { title: "3215 Treatment of Potential Payments From Medicaid Qualifying Trust", web: "", pdf: "" },
                { title: "3230 State Residence", web: "", pdf: "" },
                { title: "3240 More Liberal Income and Resource Methods", web: "", pdf: "" },
                { title: "3250 Transfer of Resources", web: "", pdf: "" },
                { title: "3255 Elimination of SSI Provision on Resources Transferred for Less Than Fair Market Value and Notification by SSA", web: "", pdf: "" },
                { title: "3256 Transfer of Resources Procedures", web: "", pdf: "" },
            ]
        },
        { title: "3257 Transfers of Assets and Treatment of Trusts Transfers of Assets for Less Than Fair Market Value", web: "", pdf: "" },
        { title: "3258. Transfers of Assets for Less Than Fair Market Value", web: "", pdf: "" },
        { title: "3259 Treatment of Trusts", web: "", pdf: "" },
        { title: "3260. Income and Resource Eligibility Rules for Certain Institutionalized Individuals and Certain Individuals Under Home and Community-Based Waivers Who Have Community Spouses", web: "", pdf: "" },
        { title: "3261. Income Eligibility", web: "", pdf: "" },
        { title: "3262. Resource Assessments and Eligibility", web: "", pdf: "" },
        { title: "3263. Notice, Hearings and Appeals", web: "", pdf: "" },
        { title: "3270. Disability Determinations Under Medicaid", web: "", pdf: "" },
        { title: "3271. Disability Determinations in §1902(f) States and SSI Criteria States", web: "", pdf: "" },
        { title: "3272. Medicaid Eligibility Quality Control (MEQC) Treatment of Payments Made During Period You Made a Reasonable Application of SSI Disability Criteria", web: "", pdf: "" },
        { title: "3273. Composition of Disability Review Teams", web: "", pdf: "" },
        { title: "3274. Procedures for Making Disability Determinations", web: "", pdf: "" },
        { title: "3275. Coordination Between State Medicaid Agency and the SSA Disability Determination Service (DDS)", web: "", pdf: "" },
        { title: "3276. Referral to SSA", web: "", pdf: "" },
        { title: "3277. Time Limit to Determine Eligibility in Disability Cases", web: "", pdf: "" },
        { title: "3280. Mandatory Coordination With WIC", web: "", pdf: "" },
        { title: "3300. Introduction", web: "", pdf: "" },
        { title: "3301. Low Income Families With Children", web: "", pdf: "" },
        { title: "3302. Individuals Deemed to Be Recipients of AFDC", web: "", pdf: "" },
        { title: "3303 Qualified Pregnant Women", web: "", pdf: "" },
        { title: "3304 Qualified Children", web: "", pdf: "" },
        { title: "3305 Deemed Eligibility of Newborns", web: "", pdf: "" },
        { title: "3306 Extended Medicaid Coverage for Pregnant Women", web: "", pdf: "" },
        { title: "3307 Continuous Eligibility", web: "", pdf: "" },
        { title: "3308 Extended Medicaid Benefits to Families Who Lose AFDC Because of Earnings From Employment or Loss of Earnings Disregards", web: "", pdf: "" },
        { title: "3309 Qualified Family Members", web: "", pdf: "" },
        { title: "3311 Mandatory Coverage for Low Income Pregnant Women and Infants", web: "", pdf: "" },
        { title: "3312 Mandatory Coverage for Low Income Children Under Age 6", web: "", pdf: "" },
        { title: "3313  Mandatory Coverage for Low Income Children Under Age 19", web: "", pdf: "" },
        { title: "3314 Extended Medicaid Benefits to Families Who Lose Eligibility Because of Income From Support Payments", web: "", pdf: "" },
        { title: "3405 Changes Due to Welfare Reform", web: "", pdf: "" },
        { title: "3410 Medicaid Eligibility for Qualified Severely Impaired Individuals and Individuals in §1619 Status", web: "", pdf: "" },
        { title: "3411 Provisions of OBRA1986 and EODAA", web: "", pdf: "" },
        { title: "3412 Operational Considerations", web: "", pdf: "" },
        { title: "3420 Individuals in States Using More Restrictive Eligibility Requirements", web: "", pdf: "" },
        { title: "3435 Persons With Drug Addiction or Alcoholism", web: "", pdf: "" },
        { title: "3485 Coverage of Qualified Disabled and Working Individuals", web: "", pdf: "" },
        { title: "3490 Coverage of Qualified Medicare Beneficiaries for Medicare Cost Sharing Expenses", web: "", pdf: "" },
        { title: "3491 Coverage of Specified Low Income Medicare Beneficiaries for Medicare Part B Premiums", web: "", pdf: "" },
        { title: "3492 Coverage of Qualifying Individuals for Medicare Part B Premiums", web: "", pdf: "" },
        { title: "3493 Medicaid Eligibility for Disabled Children Who Lose SSI Payment", web: "", pdf: "" },
        { title: "3500 Introduction", web: "", pdf: "" },
        { title: "3501 Definitions", web: "", pdf: "" },
        { title: "3502 Persons Who Meet Income and Resource Requirements for, but Do Not Receive Cash Assistance", web: "", pdf: "" },
        { title: "3503 Children Under Age 21", web: "", pdf: "" },
        { title: "3504 Reserved", web: "", pdf: "" },
        { title: "3505 Reserved", web: "", pdf: "" },
        { title: "3506 Children Under State Adoption Assistance Programs", web: "", pdf: "" },
        { title: "3570 Optional Presumptive Eligibility Period for Pregnant Women", web: "", pdf: "" },
        { title: "3571 Optional Coverage for Poor Pregnant (And Postpartum) Women, Infants and Children", web: "", pdf: "" },
        { title: "3580 Hospice Benefits", web: "", pdf: "" },
        { title: "3581 Optional Hospice Care Eligibility Group", web: "", pdf: "" },
        { title: "3582 Comparability of Hospice Care Benefits", web: "", pdf: "" },
        { title: "3583 Copayments on Hospice Care Benefits", web: "", pdf: "" },
        { title: "3584 Post-Eligibility Treatment of Income for Hospice Care", web: "", pdf: "" },
        { title: "3589 Medicaid Coverage of Home Care for Certain Disabled Children", web: "", pdf: "" },
        { title: "3590 Individuals Eligible for Services Under a Home and Community-Based Services Waiver", web: "", pdf: "" },
        { title: "3596 Optional Coverage of the Elderly and Disabled Poor for All Medicaid Benefits", web: "", pdf: "" },
        { title: "3597 Treatment of Couples in Medical Institutions", web: "", pdf: "" },
        { title: "3598 Coverage of COBRA Continuation Beneficiaries", web: "", pdf: "" },
        { title: "3599 Buy-In to Medicaid for the Working Disabled", web: "", pdf: "" },
        { title: "3600 Introduction", web: "", pdf: "" },
        { title: "3601 Background", web: "", pdf: "" },
        { title: "3610 Eligible Groups", web: "", pdf: "" },
        { title: "3611 Required Groups", web: "", pdf: "" },
        { title: "3612 Optional Eligible Groups", web: "", pdf: "" },
        { title: "3613 Criteria for Determining Categorically Needy and Medically Needy", web: "", pdf: "" },
        { title: "3620 Financial Eligibility", web: "", pdf: "" },
        { title: "3621 Single Income and Resource Standard", web: "", pdf: "" },
        { title: "3622 Cost of Living Variations", web: "", pdf: "" },
        { title: "3623 Defining Reasonable Standards", web: "", pdf: "" },
        { title: "3624 Federal Financial Participation (FFP) Limitation", web: "", pdf: "" },
        { title: "3625 Financial Methodologies", web: "", pdf: "" },
        { title: "3626 Income Eligibility", web: "", pdf: "" },
        { title: "3627 Budget Periods", web: "", pdf: "" },
        { title: "3628 Deduction of Incurred Medical and Remedial Care Expenses (Spenddown)", web: "", pdf: "" },
        { title: "3630 Resource Eligibility", web: "", pdf: "" },
        { title: "3640 Moratorium", web: "", pdf: "" },
        { title: "3645 Pay-In Spenddown Option", web: "", pdf: "" },
        { title: "3700 Introduction", web: "", pdf: "" },
        { title: "3701 General Statement of Post-Eligibility Process", web: "", pdf: "" },
        { title: "3702 Deductions From the Individual's Total Income", web: "", pdf: "" },
        { title: "3703 Required Deductions", web: "", pdf: "" },
        { title: "3704 Optional Deductions", web: "", pdf: "" },
        { title: "3705 Post-Eligibility Treatment of Certain Payments Made by the Department of Veterans Affairs", web: "", pdf: "" },
        { title: "3708 Post-Eligibility Treatment of Certain Disabled Institutionalized Individuals", web: "", pdf: "" },
        { title: "3710 Special Post-Eligibility Process for Institutionalized Persons With Community Spouses", web: "", pdf: "" },
        { title: "3711 Income Used in the Post-Eligibility Process", web: "", pdf: "" },
        { title: "3712 Mandatory Deductions From Income", web: "", pdf: "" },
        { title: "3713 Monthly Income Allowances for Community Spouses and Other Family Members", web: "", pdf: "" },
        { title: "3714 Notice, Hearings and Appeals", web: "", pdf: "" },
        { title: "3810 Medicaid Estate Recoveries", web: "", pdf: "" },
        { title: "3812 Treatment of Contributions From Relatives to Medicaid Applicants or Recipients", web: "", pdf: "" },
        { title: "3900 Third Party Liability (TPL)", web: "", pdf: "" },
        { title: "3901 Definitions", web: "", pdf: "" },
        { title: "3902 General TPL Requirements", web: "", pdf: "" },
        { title: "3903 Identification of Resources (42 CFR 433.138)", web: "", pdf: "" },
        { title: "3904 Payment of Claims (42 CFR 433.139)", web: "", pdf: "" },
        { title: "3905 Assignment of Rights to Benefits - (42 CFR 433.145)", web: "", pdf: "" },
        { title: "3906 Cooperative Agreements and Incentive Payments", web: "", pdf: "" },
        { title: "3907 Distribution of Collections", web: "", pdf: "" },
        { title: "3908 Conflicting Claims by Medicare and Medicaid", web: "", pdf: "" },
        { title: "3909 Medicare/Medicaid Crossover Claims", web: "", pdf: "" },
        { title: "3910 Medicaid Payments for Recipients Under Group Health Plans", web: "", pdf: "" },
        { title: "IM 3570 Requirements for Eligibility Under a Special Income Level", web: "", pdf: "" },
        { title: "IM 3900 Third Party Liability (TPL)", web: "", pdf: "" },
    ],
    },
    {
        id: 4,
        title: "Part 4 - Services",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_04.zip",
        subsections: [
        ],
    },
    {
        id: 5,
        title: "Part 5 - Early and Periodic Screening",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_05.zip",
        pdf: "https://web.archive.org/web/20041106222101/http://www.cms.hhs.gov/manuals/pub45pdf/smm5t.pdf",
        subsections: [
        ],
    },
    {
        id: 6,
        title: "Part 6 - Payments for Services",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_06.zip",
        pdf: "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/smm6t.pdf",
        subsections: [
        ],
    },
    {
        id: 7,
        title: "Part 7 - Quality Control",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_07.zip",
        pdf: "https://web.archive.org/web/20041106222046/http://www.cms.hhs.gov/manuals/pub45pdf/smm7t.pdf",
        subsections: [
        ],
    },
    {
        id: 8,
        title: "Part 8 - Program Integrity",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_08.zip",
        pdf: "https://web.archive.org/web/20041106221935/http://www.cms.hhs.gov/manuals/pub45pdf/smm8t.pdf",
        subsections: [
        ],
    },
    {
        id: 9,
        title: "Part 9 - Utilization Control",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_09.zip",
        pdf: "https://web.archive.org/web/20041106222347/http://www.cms.hhs.gov/manuals/pub45pdf/smm9t.pdf",
        subsections: [
        ],
    },
    {
        id: 11,
        title: "Part 11 - Medicaid Management Information System",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_11.zip",
        pdf: "https://web.archive.org/web/20041106222214/http://www.cms.hhs.gov/manuals/pub45pdf/smm11t.pdf",
        subsections: [
        ],
    },
    {
        id: 13,
        title: "Part 13 - State Plan Procedures and Preprints",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_13.zip",
        pdf: "https://web.archive.org/web/20041106222106/http://www.cms.hhs.gov/manuals/pub45pdf/smm13t.pdf",
        subsections: [
        ],
    },
    {
        id: 15,
        title: "Part 15 - Income and Eligibility Verification System",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_15.zip",
        pdf: "https://web.archive.org/web/20041106222351/http://www.cms.hhs.gov/manuals/pub45pdf/smm15t.pdf",
        subsections: [
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
                        Most of this manual has been superseded, but it may be helpful in some policy areas or for historical reference.
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
                            zipped Word documents from the current CMS website</a>. The ZIP files are the most complete version.
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
                                    <th class="table__header">Web</th>
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
    padding: 0 2rem 2rem;
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