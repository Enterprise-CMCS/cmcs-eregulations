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
        title: "Part 1 – General",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_01.zip",
        web: "https://web.archive.org/web/20020810145341/http://www.hcfa.gov:80/pubforms/45_smm/Pub45toc.htm",
        subsections: [
        { title: "Foreword", web: "https://web.archive.org/web/20010715053550/http://www.hcfa.gov/pubforms/45_smm/foreword.htm", pdf: "https://web.archive.org/web/20041106221936/http://www.cms.hhs.gov/manuals/pub45pdf/smmfwd.pdf" },
        ],
    },
    {
        id: 2,
        title: "Part 2 – State Organization and General Administration",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_02.zip",
        web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_toc.htm",
        subsections: [
            { id: 2040, title: "Appeals of State Adverse Actions for Medicaid Skilled Nursing and Intermediate Care Facilities (Not Applicable to Federal Terminations of Medicaid Facilities)", web: "https://web.archive.org/web/20010709053605/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2040_to_2040.htm", pdf: "https://web.archive.org/web/20030630065708/http://www.cms.gov:80/manuals/pub45pdf/2040.pdf" },
            { 
                id: "2080 to 2089.9",
                title: "",
                web: "https://web.archive.org/web/20010709053922/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm",
                pdf: "https://web.archive.org/web/20031210081448/http://cms.hhs.gov:80/manuals/pub45pdf/2080.pdf",
                subsections: [
                    { id: 2080, title: "Contracts Between State Agencies and Fiscal Agents, Health Care Project Grant Centers, Private Nonmedical Institutions, Health Insuring Organizations, Health Maintenance Organizations, Prepaid Health Plans and for Contracts for Automatic Data Processing Equipment/Services", web: "https://web.archive.org/web/20010709053922/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867857" },
                    { id: 2081, title: "Subcontracts", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867876" },
                    { id: 2082, title: "Specific Requirements for Fiscal Agent Contracts", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867879" },
                    { id: 2083, title: "Procurement Procedures and Policies for State Medicaid Contracts", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867883" },
                    { id: 2084, title: "Medicare and Medicaid Health and Safety Standards", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867890" },
                    { id: 2085, title: "Specific Requirements for Health Maintenance Organizations (HMOs) and Certain Health Insuring Organizations (HIOs)", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867897" },
                    { id: 2086, title: "Eligibility for FFP", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867901" },
                    { id: 2087, title: "HMO and Certain HIO Contracts - General", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867918" },
                    { id: 2088, title: "Enrollees and Benefits", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867929" },
                    { id: 2089, title: "Capitation Payments", web: "https://web.archive.org/web/20010621231345/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2080_to_2089.9.htm#_toc489867939" },
                ]
            },
            { 
                id: "2090 to 2092.9",
                title: "",
                web: "https://web.archive.org/web/20010709054313/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2090_to_2092.9.htm",
                pdf: "https://web.archive.org/web/20000929140914/http://www.hcfa.gov:80/pubforms/pub45pdf/20902.pdf",
                subsections: [
                    { id: 2090, title: "Marketing, Enrollment and Disenrollment" },
                    { id: 2091, title: "Quality Assurance" },
                    { id: 2092, title: "Additional State Agency Responsibilities" },
                ]
            },
            { 
                id: "2100 to 2106.2",
                title: "",
                web: "https://web.archive.org/web/20010709054643/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2100_to_2106.2.htm",
                pdf: "https://web.archive.org/web/20030910143952/http://cms.gov:80/manuals/pub45pdf/2100.pdf",
                subsections: [
                    { id: 2100, title: "Free Choice of Providers - General" },
                    { id: 2101, title: "Informing Beneficiaries" },
                    { id: 2102, title: "Contractual Arrangements" },
                    { id: 2103, title: "Exceptions to Freedom of Choice" },
                    { id: 2104, title: "Waiver of State Plan Requirements" },
                    { id: 2105, title: "Categories of Waivers Under §1915(b)" },
                    { id: 2106, title: "How to Submit Request for Waiver Under §1915(b)" },
                ]
            },
            { 
                id: "2106.3 to 2493",
                title: "",
                web: "https://web.archive.org/web/20010709054557/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2106.3_to_2493.htm",
                pdf: "https://web.archive.org/web/20051208033356/http://www.cms.hhs.gov:80/manuals/pub45pdf/21063.pdf",
                subsections: [
                    { id: 2106, title: "How to Submit Request for Waiver Under §1915(b)" },
                    { id: 2107, title: "Documentation Required When Submitting Requests for Waiver Under Section 1915(b)" },
                    { id: 2108, title: "Documentation of Cost Effectiveness, Access to Care, Quality of Care and Projected Impact of Waiver on the Medicaid Program" },
                    { id: 2109, title: "Requests for Modification of an Approved Waiver Program" },
                    { id: 2110, title: "Waiver Renewals" },
                    { id: 2111, title: "Monitoring, Evaluation, and Termination of Waivers" },
                    { id: 2112, title: "Freedom of Choice - Family Planning Services Under §1915(b)" },
                    { id: 2113, title: "Transportation to Providers of Services" },
                    { id: 2114, title: "Case Management for Which No Waiver Is Required" },
                    { id: 2200, title: "Requirements for Advance Directives Under State Plans for Medical Assistance" },
                    { id: 2350, title: "Legislative Background" },
                    { id: 2351, title: "State-PSRO Contracting Process" },
                    { id: 2352, title: "Plan Amendment" },
                    { id: 2353, title: "Functions Under the State-PSRO Contract" },
                    { id: 2354, title: "State Agency Jurisdiction for Hearing and Appeals" },
                    { id: 2355, title: "Responsibilities of a State That Does Not Contract With a PSRO" },
                    { id: 2356, title: "Transition Issues" },
                    { id: 2450, title: "Conflict of Interest Provisions" },
                    { id: 2451, title: "Definitions" },
                    { id: 2452, title: "Prohibited Activities" },
                    { id: 2490, title: "Claiming Federal Financial Participation (FFP) for Advance Payments Made to Providers of Medical Assistance Under Title XIX of the Social Security Actfederal Financial Participation" },
                    { id: 2493, title: "Claiming FFP for Provider Payments for State Taxes" },
                ]
            },
            { 
                id: "2495 to 2500.1",
                title: "",
                web: "https://web.archive.org/web/20010709055045/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2495_to_2500.1.htm",
                pdf: "https://web.archive.org/web/20030910235317/http://cms.gov:80/manuals/pub45pdf/2495.pdf",
                subsections: [
                    { id: 2495, title: "Maintenance of Effort" },
                    { id: 2497, title: "Documentation Required to Support a Claim for Federal" },
                    { id: 2500, title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program" },
                ]
            },
            { id: "2500.2 to 2500.6", title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program",  },
            { 
                id: "2501 to 2555",
                title: "",
                web: "https://web.archive.org/web/20010709055542/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2501_to_2555.htm",
                pdf: "https://web.archive.org/web/20030911060906/http://cms.gov:80/manuals/pub45pdf/2501.pdf",
                subsections: [
                    { id: 2501, title: "Federal Medical Assistance Percentages (FMAP) - State-by-State Tables" },
                    { id: 2502, title: "Interest on Disputed Medicaid Claims" },
                    { id: 2504, title: "Deeming and Waiver of Nurse Aide Training and Competency Evaluation Requirements" },
                    { id: 2505, title: "Nurse Aide Training and Competency Evaluation Programs and Competency Evaluation Programs" },
                    { id: 2514, title: "Federal Financial Participation (FFP) for Nurse Aide Training and Competency Evaluation Programs (NATCEPs) and Competency Evaluation Programs (CEPs)." },
                    { id: 2515, title: "Federal Financial Participation for Preadmission Screening and Annual Resident Review (PASARR) Activities" },
                    { id: 2555, title: "Information on Target Expenditure Levels, Reductions in Medicaid Payments, and Computation of Incentive Rebates to States" },
                ]
            },
            { 
                id: "2560 to 2600.2",
                title: "",
                web: "https://web.archive.org/web/20010709055530/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2560_to_2600.2.htm",
                pdf: "https://web.archive.org/web/20030911084821/http://cms.gov:80/manuals/pub45pdf/2560.pdf",
                subsections: [
                    { id: 2560, title: "Medicaid Funding Limitations Policy" },
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                ]
            },
            { id: "2600.3 to 2600.10", title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program", web: "https://web.archive.org/web/20010709060622/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2600_to_2600.10.htm", pdf: "https://web.archive.org/web/20000929140950/http://www.hcfa.gov:80/pubforms/pub45pdf/26003.pdf" },
            { 
                id: "2600.11 to 2602",
                title: "",
                web: "https://web.archive.org/web/20010709060133/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2600.11_to_2602.htm",
                subsections: [
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                    { id: 2602, title: "Submission Schedule - Medicaid Program Budget Report (Form HCFA-25)" },
                ]
            },
            { id: "2700 to 2700.2", title: "Federal Reporting Requirements", web: "https://web.archive.org/web/20010709061515/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700_to_2700.2.htm", pdf: "https://web.archive.org/web/20030910161000/http://cms.gov:80/manuals/pub45pdf/2700.pdf" },
            { id: "2700.4", title: "Federal Reporting Requirements", web: "https://web.archive.org/web/20010709060532/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700.4_to_2700.4.htm", pdf: "https://web.archive.org/web/20030910202813/http://cms.gov:80/manuals/pub45pdf/27004.pdf" },
            { id: "2700.6", title: "Federal Reporting Requirements", web: "https://web.archive.org/web/20010709061449/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2700.6_to_2700.6.htm", pdf: "https://web.archive.org/web/20000929141011/http://www.hcfa.gov:80/pubforms/pub45pdf/27006.pdf" },
            { 
                id: "2850 to 2853.5",
                title: "",
                web: "https://web.archive.org/web/20010709050741/http://www.hcfa.gov/pubforms/45_smm/sm_02_2_2850_to_2853.5.htm",
                pdf: "https://web.archive.org/web/20000929141015/http://www.hcfa.gov:80/pubforms/pub45pdf/2850.pdf",
                subsections: [
                    { id: 2850, title: "Withholding the Federal Share of Payments to Medicaid Providers to Recover Medicare Overpayments; Withholding Medicare Payments to Recover Medicaid Overpayments" },
                    { id: 2851, title: "Procedures Required of the Medicaid State Agency to Implement Section 1914" },
                    { id: 2852, title: "Procedures Required of the Medicaid State Agency to Implement Section 1885" },
                    { id: 2853, title: "Procedures for Refunding the Federal Share of Medicaid Overpayments" },
                ]
            },
            { 
                id: "2900.2 to 2975.6",
                title: "",
                web: "https://web.archive.org/web/20020805231110/http://www.hcfa.gov:80/pubforms/45_smm/sm_02_2_2900.2_to_2975.6.htm",
                pdf: "https://web.archive.org/web/20000929141021/http://www.hcfa.gov:80/pubforms/pub45pdf/2900.pdf",
                subsections: [
                    { id: 2900, title: "Fair Hearings and Appeals" },
                    { id: 2901, title: "Notice and Opportunity for a Fair Hearing" },
                    { id: 2902, title: "Hearings" },
                    { id: 2903, title: "Hearing Decision" },
                    { id: 2904, title: "Reopening and Recovery" },
                    { id: 2905, title: "Outstationing of Eligibility Workers General" },
                    { id: 2906, title: "Outstation Locations" },
                    { id: 2907, title: "Staffing at Outstation Locations" },
                    { id: 2908, title: "Guidelines for Outstationing and Providing Application Assistance at Low Use Locations" },
                    { id: 2909, title: "Limitations on Outstationed Eligibility Workers" },
                    { id: 2910, title: "Application Process" },
                    { id: 2911, title: "Applications" },
                    { id: 2912, title: "Compliance With Federal Regulations" },
                    { id: 2913, title: "FFP for Outstationing" },
                    { id: 2975, title: "Contingency Fee Reimbursement for Third Party Liability Identification or Collection" },
                ]
            },
        ],
    },
    {
        id: 3,
        title: "Part 3 – Eligibility",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_03.zip",
        web: "https://web.archive.org/web/20010621231541/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_toc.htm",
        subsections: [
        { 
            id: "3200 to 3207",
            title: "",
            web: "https://web.archive.org/web/20010715053855/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3200_to_3207.htm",
            pdf: "https://web.archive.org/web/20000929141030/http://www.hcfa.gov:80/pubforms/pub45pdf/sm3200.pdf",
            subsections: [
                { id: 3200, title: "Changes Due to Welfare Reform", web: "", pdf: "" },
                { id: 3207, title: "Changes in SSI Definition of Disability Due to Welfare Reform", web: "", pdf: "" },
            ]
        },
        { 
            id: "3210 to 3256",
            title: "",
            web: "https://web.archive.org/web/20010715054127/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3210_to_3256.htm",
            pdf: "https://web.archive.org/web/20030808034231/http://www.cms.hhs.gov/manuals/pub45pdf/sm3210.pdf",
            subsections: [
                { id: 3210, title: "Citizenship and Alienage", web: "", pdf: "" },
                { id: 3211, title: "Aliens", web: "", pdf: "" },
                { id: 3212, title: "Documentation and Verification of Status as Citizen or Alien", web: "", pdf: "" },
                { id: 3213, title: "Redeterminations and FFP Availability", web: "", pdf: "" },
                { id: 3215, title: "Treatment of Potential Payments From Medicaid Qualifying Trust", web: "", pdf: "" },
                { id: 3230, title: "State Residence", web: "", pdf: "" },
                { id: 3240, title: "More Liberal Income and Resource Methods", web: "", pdf: "" },
                { id: 3250, title: "Transfer of Resources", web: "", pdf: "" },
                { id: 3255, title: "Elimination of SSI Provision on Resources Transferred for Less Than Fair Market Value and Notification by SSA", web: "", pdf: "" },
                { id: 3256, title: "Transfer of Resources Procedures", web: "", pdf: "" },
            ]
        },
        { 
            id: "3257 to 3259.8",
            title: "",
            web: "https://web.archive.org/web/20010715054448/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3257_to_3259.8.htm",
            pdf: "https://web.archive.org/web/20040625034414/http://cms.hhs.gov:80/manuals/pub45pdf/sm3257.pdf",
            subsections: [
                { id: 3257, title: "Transfers of Assets and Treatment of Trusts Transfers of Assets for Less Than Fair Market Value", web: "", pdf: "" },
                { id: 3258, title: "Transfers of Assets for Less Than Fair Market Value", web: "", pdf: "" },
                { id: 3259, title: "Treatment of Trusts", web: "", pdf: "" },
            ]
        },
        { 
            id: "3260 to 3280.2",
            title: "",
            web: "https://web.archive.org/web/20010822192630/http://www.hcfa.gov/pubforms/45_smm/sm_03_3260.htm",
            pdf: "https://web.archive.org/web/20030910145847/http://cms.gov:80/manuals/pub45pdf/sm3260.pdf",
            subsections: [
                { id: 3260, title: "Income and Resource Eligibility Rules for Certain Institutionalized Individuals and Certain Individuals Under Home and Community-Based Waivers Who Have Community Spouses", web: "", pdf: "" },
                { id: 3261, title: "Income Eligibility", web: "", pdf: "" },
                { id: 3262, title: "Resource Assessments and Eligibility", web: "", pdf: "" },
                { id: 3263, title: "Notice, Hearings and Appeals", web: "", pdf: "" },
                { id: 3270, title: "Disability Determinations Under Medicaid", web: "", pdf: "" },
                { id: 3271, title: "Disability Determinations in §1902(f) States and SSI Criteria States", web: "", pdf: "" },
                { id: 3272, title: "Medicaid Eligibility Quality Control (MEQC) Treatment of Payments Made During Period You Made a Reasonable Application of SSI Disability Criteria", web: "", pdf: "" },
                { id: 3273, title: "Composition of Disability Review Teams", web: "", pdf: "" },
                { id: 3274, title: "Procedures for Making Disability Determinations", web: "", pdf: "" },
                { id: 3275, title: "Coordination Between State Medicaid Agency and the SSA Disability Determination Service (DDS)", web: "", pdf: "" },
                { id: 3276, title: "Referral to SSA", web: "", pdf: "" },
                { id: 3277, title: "Time Limit to Determine Eligibility in Disability Cases", web: "", pdf: "" },
                { id: 3280, title: "Mandatory Coordination With WIC", web: "", pdf: "" },        
            ]
        },
        { 
            id: "3300 to 3314.2",
            title: "",
            web: "https://web.archive.org/web/20010822194107/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3300_to_3314.2.htm",
            pdf: "https://web.archive.org/web/20030910181119/http://cms.gov:80/manuals/pub45pdf/sm3300.pdf",
            subsections: [
                { id: 3300, title: "Introduction", web: "", pdf: "" },
                { id: 3301, title: "Low Income Families With Children", web: "", pdf: "" },
                { id: 3302, title: "Individuals Deemed to Be Recipients of AFDC", web: "", pdf: "" },
                { id: 3303, title: "Qualified Pregnant Women", web: "", pdf: "" },
                { id: 3304, title: "Qualified Children", web: "", pdf: "" },
                { id: 3305, title: "Deemed Eligibility of Newborns", web: "", pdf: "" },
                { id: 3306, title: "Extended Medicaid Coverage for Pregnant Women", web: "", pdf: "" },
                { id: 3307, title: "Continuous Eligibility", web: "", pdf: "" },
                { id: 3308, title: "Extended Medicaid Benefits to Families Who Lose AFDC Because of Earnings From Employment or Loss of Earnings Disregards", web: "", pdf: "" },
                { id: 3309, title: "Qualified Family Members", web: "", pdf: "" },
                { id: 3311, title: "Mandatory Coverage for Low Income Pregnant Women and Infants", web: "", pdf: "" },
                { id: 3312, title: "Mandatory Coverage for Low Income Children Under Age 6", web: "", pdf: "" },
                { id: 3313, title: " Mandatory Coverage for Low Income Children Under Age 19", web: "", pdf: "" },
                { id: 3314, title: "Extended Medicaid Benefits to Families Who Lose Eligibility Because of Income From Support Payments", web: "", pdf: "" },
            ]
        },
        { id: 3405, title: "Changes Due to Welfare Reform", web: "https://web.archive.org/web/20010822164014/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3405_to_3405.htm", pdf: "https://web.archive.org/web/20030910213015/http://cms.gov:80/manuals/pub45pdf/sm3405.pdf" },
        { 
            id: "3410 to 3493",
            title: "",
            web: "https://web.archive.org/web/20010822163907/http://www.hcfa.gov/pubforms/45_smm/sm_03_3_3410_to_3493.htm",
            pdf: "https://web.archive.org/web/20031127050455/http://www.cms.gov:80/manuals/pub45pdf/sm3410.pdf",
            subsections: [
                { id: 3410, title: "Medicaid Eligibility for Qualified Severely Impaired Individuals and Individuals in §1619 Status", web: "", pdf: "" },
                { id: 3411, title: "Provisions of OBRA1986 and EODAA", web: "", pdf: "" },
                { id: 3412, title: "Operational Considerations", web: "", pdf: "" },
                { id: 3420, title: "Individuals in States Using More Restrictive Eligibility Requirements", web: "", pdf: "" },
                { id: 3435, title: "Persons With Drug Addiction or Alcoholism", web: "", pdf: "" },
                { id: 3485, title: "Coverage of Qualified Disabled and Working Individuals", web: "", pdf: "" },
                { id: 3490, title: "Coverage of Qualified Medicare Beneficiaries for Medicare Cost Sharing Expenses", web: "", pdf: "" },
                { id: 3491, title: "Coverage of Specified Low Income Medicare Beneficiaries for Medicare Part B Premiums", web: "", pdf: "" },
                { id: 3492, title: "Coverage of Qualifying Individuals for Medicare Part B Premiums", web: "", pdf: "" },
                { id: 3493, title: "Medicaid Eligibility for Disabled Children Who Lose SSI Payment", web: "", pdf: "" },        
            ]
        },
        { id: 3500, title: "Introduction", web: "", pdf: "" },
        { id: 3501, title: "Definitions", web: "", pdf: "" },
        { id: 3502, title: "Persons Who Meet Income and Resource Requirements for, but Do Not Receive Cash Assistance", web: "", pdf: "" },
        { id: 3503, title: "Children Under Age 21", web: "", pdf: "" },
        { id: 3504, title: "Reserved", web: "", pdf: "" },
        { id: 3505, title: "Reserved", web: "", pdf: "" },
        { id: 3506, title: "Children Under State Adoption Assistance Programs", web: "", pdf: "" },
        { id: 3570, title: "Optional Presumptive Eligibility Period for Pregnant Women", web: "", pdf: "" },
        { id: 3571, title: "Optional Coverage for Poor Pregnant (And Postpartum) Women, Infants and Children", web: "", pdf: "" },
        { id: 3580, title: "Hospice Benefits", web: "", pdf: "" },
        { id: 3581, title: "Optional Hospice Care Eligibility Group", web: "", pdf: "" },
        { id: 3582, title: "Comparability of Hospice Care Benefits", web: "", pdf: "" },
        { id: 3583, title: "Copayments on Hospice Care Benefits", web: "", pdf: "" },
        { id: 3584, title: "Post-Eligibility Treatment of Income for Hospice Care", web: "", pdf: "" },
        { id: 3589, title: "Medicaid Coverage of Home Care for Certain Disabled Children", web: "", pdf: "" },
        { id: 3590, title: "Individuals Eligible for Services Under a Home and Community-Based Services Waiver", web: "", pdf: "" },
        { id: 3596, title: "Optional Coverage of the Elderly and Disabled Poor for All Medicaid Benefits", web: "", pdf: "" },
        { id: 3597, title: "Treatment of Couples in Medical Institutions", web: "", pdf: "" },
        { id: 3598, title: "Coverage of COBRA Continuation Beneficiaries", web: "", pdf: "" },
        { id: 3599, title: "Buy-In to Medicaid for the Working Disabled", web: "", pdf: "" },
        { id: 3600, title: "Introduction", web: "", pdf: "" },
        { id: 3601, title: "Background", web: "", pdf: "" },
        { id: 3610, title: "Eligible Groups", web: "", pdf: "" },
        { id: 3611, title: "Required Groups", web: "", pdf: "" },
        { id: 3612, title: "Optional Eligible Groups", web: "", pdf: "" },
        { id: 3613, title: "Criteria for Determining Categorically Needy and Medically Needy", web: "", pdf: "" },
        { id: 3620, title: "Financial Eligibility", web: "", pdf: "" },
        { id: 3621, title: "Single Income and Resource Standard", web: "", pdf: "" },
        { id: 3622, title: "Cost of Living Variations", web: "", pdf: "" },
        { id: 3623, title: "Defining Reasonable Standards", web: "", pdf: "" },
        { id: 3624, title: "Federal Financial Participation (FFP) Limitation", web: "", pdf: "" },
        { id: 3625, title: "Financial Methodologies", web: "", pdf: "" },
        { id: 3626, title: "Income Eligibility", web: "", pdf: "" },
        { id: 3627, title: "Budget Periods", web: "", pdf: "" },
        { id: 3628, title: "Deduction of Incurred Medical and Remedial Care Expenses (Spenddown)", web: "", pdf: "" },
        { id: 3630, title: "Resource Eligibility", web: "", pdf: "" },
        { id: 3640, title: "Moratorium", web: "", pdf: "" },
        { id: 3645, title: "Pay-In Spenddown Option", web: "", pdf: "" },
        { id: 3700, title: "Introduction", web: "", pdf: "" },
        { id: 3701, title: "General Statement of Post-Eligibility Process", web: "", pdf: "" },
        { id: 3702, title: "Deductions From the Individual's Total Income", web: "", pdf: "" },
        { id: 3703, title: "Required Deductions", web: "", pdf: "" },
        { id: 3704, title: "Optional Deductions", web: "", pdf: "" },
        { id: 3705, title: "Post-Eligibility Treatment of Certain Payments Made by the Department of Veterans Affairs", web: "", pdf: "" },
        { id: 3708, title: "Post-Eligibility Treatment of Certain Disabled Institutionalized Individuals", web: "", pdf: "" },
        { id: 3710, title: "Special Post-Eligibility Process for Institutionalized Persons With Community Spouses", web: "", pdf: "" },
        { id: 3711, title: "Income Used in the Post-Eligibility Process", web: "", pdf: "" },
        { id: 3712, title: "Mandatory Deductions From Income", web: "", pdf: "" },
        { id: 3713, title: "Monthly Income Allowances for Community Spouses and Other Family Members", web: "", pdf: "" },
        { id: 3714, title: "Notice, Hearings and Appeals", web: "", pdf: "" },
        { id: 3810, title: "Medicaid Estate Recoveries", web: "", pdf: "" },
        { id: 3812, title: "Treatment of Contributions From Relatives to Medicaid Applicants or Recipients", web: "", pdf: "" },
        { id: 3900, title: "Third Party Liability (TPL)", web: "", pdf: "" },
        { id: 3901, title: "Definitions", web: "", pdf: "" },
        { id: 3902, title: "General TPL Requirements", web: "", pdf: "" },
        { id: 3903, title: "Identification of Resources (42 CFR 433.138)", web: "", pdf: "" },
        { id: 3904, title: "Payment of Claims (42 CFR 433.139)", web: "", pdf: "" },
        { id: 3905, title: "Assignment of Rights to Benefits - (42 CFR 433.145)", web: "", pdf: "" },
        { id: 3906, title: "Cooperative Agreements and Incentive Payments", web: "", pdf: "" },
        { id: 3907, title: "Distribution of Collections", web: "", pdf: "" },
        { id: 3908, title: "Conflicting Claims by Medicare and Medicaid", web: "", pdf: "" },
        { id: 3909, title: "Medicare/Medicaid Crossover Claims", web: "", pdf: "" },
        { id: 3910, title: "Medicaid Payments for Recipients Under Group Health Plans", web: "", pdf: "" },
        { id: "IM 3570", title: "Requirements for Eligibility Under a Special Income Level", web: "", pdf: "" },
        { id: "IM 3900", title: "Third Party Liability (TPL)", web: "", pdf: "" },
    ],
    },
    {
        id: 4,
        title: "Part 4 – Services",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_04.zip",
        web: "https://web.archive.org/web/20010621232604/http://www.hcfa.gov/pubforms/45_smm/sm_04_4_toc.htm",
        subsections: [
        ],
    },
    {
        id: 5,
        title: "Part 5 – Early and Periodic Screening",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_05.zip",
        pdf: "https://web.archive.org/web/20041106222101/http://www.cms.hhs.gov/manuals/pub45pdf/smm5t.pdf",
        web: "https://web.archive.org/web/20011108011722/http://www.hcfa.gov/pubforms/45_smm/sm_05_5_5010_to_5360with_toc.htm",
        subsections: [
        ],
    },
    {
        id: 6,
        title: "Part 6 – Payments for Services",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_06.zip",
        pdf: "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/smm6t.pdf",
        web: "https://web.archive.org/web/20010621234011/http://www.hcfa.gov/pubforms/45_smm/sm_06_6_toc.htm",
        subsections: [
        ],
    },
    {
        id: 7,
        title: "Part 7 – Quality Control",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_07.zip",
        pdf: "https://web.archive.org/web/20041106222046/http://www.cms.hhs.gov/manuals/pub45pdf/smm7t.pdf",
        web: "https://web.archive.org/web/20010621234142/http://www.hcfa.gov/pubforms/45_smm/sm_07_7_toc.htm",
        subsections: [
        ],
    },
    {
        id: 8,
        title: "Part 8 – Program Integrity",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_08.zip",
        pdf: "https://web.archive.org/web/20041106221935/http://www.cms.hhs.gov/manuals/pub45pdf/smm8t.pdf",
        web: "https://web.archive.org/web/20010621235218/http://www.hcfa.gov/pubforms/45_smm/sm_08_8_8001_to_8003with_toc.htm",
        subsections: [
        ],
    },
    {
        id: 9,
        title: "Part 9 – Utilization Control",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_09.zip",
        pdf: "https://web.archive.org/web/20041106222347/http://www.cms.hhs.gov/manuals/pub45pdf/smm9t.pdf",
        web: "https://web.archive.org/web/20010810145526/http://www.hcfa.gov/pubforms/45_smm/sm_09_9_toc.htm",
        subsections: [
        ],
    },
    {
        id: 11,
        title: "Part 11 – Medicaid Management Information System",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_11.zip",
        pdf: "https://web.archive.org/web/20041106222214/http://www.cms.hhs.gov/manuals/pub45pdf/smm11t.pdf",
        web: "https://web.archive.org/web/20010124063900/http://www.hcfa.gov/pubforms/45_smm/sm_11_11_toc.htm",
        subsections: [
        ],
    },
    {
        id: 13,
        title: "Part 13 – State Plan Procedures and Preprints",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_13.zip",
        pdf: "https://web.archive.org/web/20041106222106/http://www.cms.hhs.gov/manuals/pub45pdf/smm13t.pdf",
        web: "https://web.archive.org/web/20010622001357/http://www.hcfa.gov/pubforms/45_smm/sm_13_13_toc.htm",
        subsections: [
        ],
    },
    {
        id: 15,
        title: "Part 15 - Income and Eligibility Verification System",
        zip: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_15.zip",
        web: "https://web.archive.org/web/20010413170015/http://www.hcfa.gov/pubforms/45_smm/sm_15_15_toc.htm",
        pdf: "https://web.archive.org/web/20041106222351/http://www.cms.hhs.gov/manuals/pub45pdf/smm15t.pdf",
        subsections: [
        ],
    },
]);

const expanded = ref({});
const toggleExpand = (id) => {
    expanded.value[id] = !expanded.value[id];
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
        <div id="manualApp" class="site-container">
            <Banner title="State Medicaid Manual" />
            <div id="main-content" class="manual__container">
                <div class="content no-sidebar">
                    <p class="manual-page-description">
                        This page links to 
                        <a 
                            class="external"
                            target="_blank"
                            href="
                            https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927
                            ">
                            zipped Word documents from the CMS website</a>,
                        along with 
                            <a 
                            class="external"
                            target="_blank"
                            href="
                            https://web.archive.org/web/20010609052207/http://www.hcfa.gov/pubforms/45_smm/pub45toc.htm
                            ">web pages</a> 
                        and <a
                            class="external"
                            target="_blank"
                            href="
                            https://web.archive.org/web/20050204151206/http://www.cms.hhs.gov:80/manuals/pub45pdf/smmtoc.asp
                            ">PDFs</a>
                        from archived copies of the CMS website. 
                        The ZIP files are the most current and complete version.
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
                                    <th class="table__header">
                                        <div class="cell__title">Part/Section</div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">Word (ZIP)</div>
                                        <div class="cell__subtitle">Current; last updated 2015</div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">Web</div>
                                        <div class="cell__subtitle">Archived 2001-2004</div>
                                    </th>
                                    <th class="table__header">
                                        <div class="cell__title">PDF</div>
                                        <div class="cell__subtitle">Archived 2000-2005</div>
                                    </th>
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
                                            <span v-if="section.id || section.title" :class="['section-text', { 'section-link': section.subsections }]" @click="section.subsections && toggleExpand(section.id)">
                                                <span>{{ section.title }}</span>
                                            </span>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.zip" :href="section.zip" target="_blank" class="link-btn">Word</a>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.web" :href="section.web" target="_blank" class="link-btn">Web</a>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.pdf" :href="section.pdf" target="_blank" class="link-btn">PDF</a>
                                        </td>
                                    </tr>
                                    <template v-if="expanded[section.id] && section.subsections">
                                        <template v-for="sub in section.subsections" :key="sub.id">
                                            <tr class="table__row table__row--body subsection-row">
                                                <td class="table__cell subsection-cell">
                                                    <button v-if="sub.subsections" class="expand-btn" @click="toggleExpand(sub.id)">
                                                        <span>{{ expanded[sub.id] ? '▼' : '▶' }}</span>
                                                    </button>
                                                    <span v-if="sub.id || sub.title" :class="['section-text', { 'section-link': sub.subsections }]" @click="sub.subsections && toggleExpand(sub.id)">
                                                        <span v-if="sub.id" class="section-number">{{ sub.id }}{{ sub.title ? '.' : '' }}</span> <span>{{ sub.title }}</span>
                                                    </span>
                                                </td>
                                                <td class="table__cell"></td>
                                                <td class="table__cell">
                                                    <a v-if="sub.web" :href="sub.web" target="_blank" class="link-btn">Web</a>
                                                </td>
                                                <td class="table__cell">
                                                    <a v-if="sub.pdf" :href="sub.pdf" target="_blank" class="link-btn">PDF</a>
                                                </td>
                                            </tr>
                                            <template v-if="sub.subsections && expanded[sub.id]">
                                                <tr v-for="nestedSub in sub.subsections" 
                                                    :key="nestedSub.id"
                                                    class="table__row table__row--body nested-subsection-row">
                                                    <td class="table__cell nested-subsection-cell">
                                                        <span v-if="nestedSub.id || nestedSub.title" :class="['section-text', { 'section-link': nestedSub.subsections }]" @click="nestedSub.subsections && toggleExpand(nestedSub.id)">
                                                            <span v-if="nestedSub.id" class="section-number">{{ nestedSub.id }}{{ nestedSub.title ? '.' : '' }}</span> <span>{{ nestedSub.title }}</span>
                                                        </span>
                                                    </td>
                                                    <td class="table__cell"></td>
                                                    <td class="table__cell">
                                                        <a v-if="nestedSub.web" :href="nestedSub.web" target="_blank" class="link-btn">Web</a>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a v-if="nestedSub.pdf" :href="nestedSub.pdf" target="_blank" class="link-btn">PDF</a>
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
    padding: 0 2rem 0 2rem;
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
    background-color: #254c68;
    border-bottom: 2px solid #dee2e6;
    font-weight: 700;
    color: #fff;
}

/* Add fixed widths for specific columns */
.table__header:nth-child(2),
.table__header:nth-child(3),
.table__header:nth-child(4) {
    width: 120px;
}

.cell__subtitle {
    font-weight: normal;
    font-style: italic;
    font-size: 14px;
}

.table__cell {
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
}

/* Add fixed widths for specific columns */
.table__cell:nth-child(2),
.table__cell:nth-child(3),
.table__cell:nth-child(4) {
    width: 120px;
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

.section-text {
    text-decoration: none;
}

.section-link {
    cursor: pointer;
}

.section-number {
    font-weight: 600;
}

</style> 