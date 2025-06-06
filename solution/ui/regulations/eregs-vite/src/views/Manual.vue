<script setup>
import { inject, ref } from "vue";
import { useRoute } from "vue-router";

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
        title: "Foreword",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_01.zip",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041213113453/http://www.cms.hhs.gov/manuals/45_smm/foreword.asp",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106221936/http://www.cms.hhs.gov/manuals/pub45pdf/smmfwd.pdf",
            date: ""
        }
    },
    {
        id: 2,
        title: "Part 2 – State Organization and General Administration",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_02.zip",
            date: "2000"
        },
        web: {
            url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_toc.asp",
            date: "2000"
        },
        pdf: { date: "" },
        subsections: [
            {
                id: 2040,
                title: "Appeals of State Adverse Actions for Medicaid Skilled Nursing and Intermediate Care Facilities (Not Applicable to Federal Terminations of Medicaid Facilities)",
                zip: {
                    date: "1986"
                },
                web: {
                    url: "https://web.archive.org/web/20041211221927/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2040_to_2040.asp",
                    date: "1986"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030630065708/http://www.cms.gov:80/manuals/pub45pdf/2040.pdf",
                    date: "1986"
                }
            },
            {
                id: "2080 to 2089.9",
                title: "",
                zip: {
                    date: "2000"
                },
                web: {
                    url: "https://web.archive.org/web/20041211222603/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp",
                    date: "2000"
                },
                pdf: {
                    url: "https://web.archive.org/web/20031210081448/http://cms.hhs.gov:80/manuals/pub45pdf/2080.pdf",
                    date: "1993"
                },
                subsections: [
                    { id: 2080, title: "Contracts Between State Agencies and Fiscal Agents, Health Care Project Grant Centers, Private Nonmedical Institutions, Health Insuring Organizations, Health Maintenance Organizations, Prepaid Health Plans and for Contracts for Automatic Data Processing Equipment/Services", web: {
                        /*url: "https://web.archive.org/web/20041211222603/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867857",*/
                        date: ""
                    } },
                    { id: 2081, title: "Subcontracts", web: {
                        /*url: "https://web.archive.org/web/20041211222603/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867876",*/
                        date: ""
                    } },
                    { id: 2082, title: "Specific Requirements for Fiscal Agent Contracts", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867879",*/
                        date: ""
                    } },
                    { id: 2083, title: "Procurement Procedures and Policies for State Medicaid Contracts", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867883",*/
                        date: ""
                    } },
                    { id: 2084, title: "Medicare and Medicaid Health and Safety Standards", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867890",*/
                        date: ""
                    } },
                    { id: 2085, title: "Specific Requirements for Health Maintenance Organizations (HMOs) and Certain Health Insuring Organizations (HIOs)", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867897",*/
                        date: ""
                    } },
                    { id: 2086, title: "Eligibility for FFP", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867901",*/
                        date: ""
                    } },
                    { id: 2087, title: "HMO and Certain HIO Contracts - General", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867918",*/
                        date: ""
                    } },
                    { id: 2088, title: "Enrollees and Benefits", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867929",*/
                        date: ""
                    } },
                    { id: 2089, title: "Capitation Payments", web: {
                        /*url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867939",*/
                        date: ""
                    } },
                ]
            },
            {
                id: "2090 to 2092.9",
                title: "",
                zip: { date: "1992" },
                web: {
                    url: "https://web.archive.org/web/20041211221428/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2090_to_2092.9.asp",
                    date: "1992"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929140914/http://www.hcfa.gov:80/pubforms/pub45pdf/20902.pdf",
                    date: "1992"
                },
                subsections: [
                    { id: 2090, title: "Marketing, Enrollment and Disenrollment" },
                    { id: 2091, title: "Quality Assurance" },
                    { id: 2092, title: "Additional State Agency Responsibilities" },
                ]
            },
            {
                id: "2100 to 2106.2",
                title: "",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041211221711/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2100_to_2106.2.asp",
                    date: "1994"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910143952/http://cms.gov:80/manuals/pub45pdf/2100.pdf",
                    date: "1994"
                },
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
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041211222317/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2106.3_to_2493.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20051208033356/http://www.cms.hhs.gov:80/manuals/pub45pdf/21063.pdf",
                    date: "1991"
                },
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
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041211220824/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2495_to_2500.1.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910235317/http://cms.gov:80/manuals/pub45pdf/2495.pdf",
                    date: "1991"
                },
                subsections: [
                    { id: 2495, title: "Maintenance of Effort" },
                    { id: 2497, title: "Documentation Required to Support a Claim for Federal Financial Participation" },
                    { id: 2500, title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program" },
                ]
            },
            {
                id: "2500.2 to 2500.6",
                title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program",
                zip: { date: 1991 },
                web: { date: "unavailable" },
                pdf: { date: "unavailable" },
            },
            {
                id: "2501 to 2555",
                title: "",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041211221703/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2501_to_2555.asp",
                    date: "1992"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911060906/http://cms.gov:80/manuals/pub45pdf/2501.pdf",
                    date: "1992"
                },
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
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041211222048/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2560_to_2600.2.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911084821/http://cms.gov:80/manuals/pub45pdf/2560.pdf",
                    date: "1991"
                },
                subsections: [
                    { id: 2560, title: "Medicaid Funding Limitations Policy" },
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                ]
            },
            {
                id: "2600.3 to 2600.10",
                title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041211221749/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2600_to_2600.10.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929140950/http://www.hcfa.gov:80/pubforms/pub45pdf/26003.pdf",
                    date: "1991"
                }
            },
            {
                id: "2600.11 to 2602",
                title: "",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041211221327/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2600.11_to_2602.asp",
                    date: "1991"
                },
                pdf: { date: "unavailable" },
                subsections: [
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program" },
                    { id: 2602, title: "Submission Schedule - Medicaid Program Budget Report (Form HCFA-25)" },
                ]
            },
            {
                id: "2700 to 2700.2",
                title: "Federal Reporting Requirements",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041211221832/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700_to_2700.2.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910161000/http://cms.gov:80/manuals/pub45pdf/2700.pdf",
                    date: "1998"
                }
            },
            {
                id: "2700.4",
                title: "Federal Reporting Requirements",
                zip: { date: 1996 },
                web: {
                    url: "https://web.archive.org/web/20041211222643/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700.4_to_2700.4.asp",
                    date: "1996"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910202813/http://cms.gov:80/manuals/pub45pdf/27004.pdf",
                    date: "1996"
                }
            },
            {
                id: "2700.6",
                title: "Federal Reporting Requirements",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041211050529/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700.6_to_2700.6.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141011/http://www.hcfa.gov:80/pubforms/pub45pdf/27006.pdf",
                    date: "1998"
                }
            },
            {
                id: "2850 to 2853.5",
                title: "",
                zip: { date: 1986 },
                web: {
                    url: "https://web.archive.org/web/20041211164736/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2850_to_2853.5.asp",
                    date: "1986"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141015/http://www.hcfa.gov:80/pubforms/pub45pdf/2850.pdf",
                    date: "1986"
                },
                subsections: [
                    { id: 2850, title: "Withholding the Federal Share of Payments to Medicaid Providers to Recover Medicare Overpayments; Withholding Medicare Payments to Recover Medicaid Overpayments" },
                    { id: 2851, title: "Procedures Required of the Medicaid State Agency to Implement Section 1914" },
                    { id: 2852, title: "Procedures Required of the Medicaid State Agency to Implement Section 1885" },
                    { id: 2853, title: "Procedures for Refunding the Federal Share of Medicaid Overpayments" },
                ]
            },
            {
                id: "2900.2 to 2975.6",
                zip: { date: 1991 },
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211222256/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2900.2_to_2975.6.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141021/http://www.hcfa.gov:80/pubforms/pub45pdf/2900.pdf",
                    date: "1991"
                },
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
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_03.zip",
            date: "2015"
        },
        web: {
            url: "https://web.archive.org/web/20041106182006/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_toc.asp",
            date: "2001"
        },
        subsections: [
            {
                id: "3200 to 3207",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20041212152429/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3200_to_3207.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141030/http://www.hcfa.gov:80/pubforms/pub45pdf/sm3200.pdf",
                    date: "1997"
                },
                zip: { date: "1997" },
                subsections: [
                    { id: 3200, title: "Changes Due to Welfare Reform" },
                    { id: 3207, title: "Changes in SSI Definition of Disability Due to Welfare Reform" },
                ]
            },
            {
                id: "3210 to 3256",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20041213002635/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3210_to_3256.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030808034231/http://www.cms.hhs.gov/manuals/pub45pdf/sm3210.pdf",
                    date: "1997"
                },
                zip: { date: "1997" },
                subsections: [
                    { id: 3210, title: "Citizenship and Alienage" },
                    { id: 3211, title: "Aliens" },
                    { id: 3212, title: "Documentation and Verification of Status as Citizen or Alien" },
                    { id: 3213, title: "Redeterminations and FFP Availability" },
                    { id: 3215, title: "Treatment of Potential Payments From Medicaid Qualifying Trust" },
                    { id: 3230, title: "State Residence" },
                    { id: 3240, title: "More Liberal Income and Resource Methods" },
                    { id: 3250, title: "Transfer of Resources" },
                    { id: 3255, title: "Elimination of SSI Provision on Resources Transferred for Less Than Fair Market Value and Notification by SSA" },
                    { id: 3256, title: "Transfer of Resources Procedures" },
                ]
            },
            {
                id: "3257 to 3259.8",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20041213121554/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3257_to_3259.8.asp",
                    date: "1994"
                },
                pdf: {
                    url: "https://web.archive.org/web/20040625034414/http://cms.hhs.gov:80/manuals/pub45pdf/sm3257.pdf",
                    date: "1994"
                },
                zip: { date: "1994" },
                subsections: [
                    { id: 3257, title: "Transfers of Assets and Treatment of Trusts Transfers of Assets for Less Than Fair Market Value" },
                    { id: 3258, title: "Transfers of Assets for Less Than Fair Market Value" },
                    { id: 3259, title: "Treatment of Trusts" },
                ]
            },
            {
                id: "3260 to 3280.2",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20040808075206/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3260.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910145847/http://cms.gov:80/manuals/pub45pdf/sm3260.pdf",
                    date: "1991"
                },
                zip: { date: "1991" },
                subsections: [
                    { id: 3260, title: "Income and Resource Eligibility Rules for Certain Institutionalized Individuals and Certain Individuals Under Home and Community-Based Waivers Who Have Community Spouses" },
                    { id: 3261, title: "Income Eligibility" },
                    { id: 3262, title: "Resource Assessments and Eligibility" },
                    { id: 3263, title: "Notice, Hearings and Appeals" },
                    { id: 3270, title: "Disability Determinations Under Medicaid" },
                    { id: 3271, title: "Disability Determinations in §1902(f) States and SSI Criteria States" },
                    { id: 3272, title: "Medicaid Eligibility Quality Control (MEQC) Treatment of Payments Made During Period You Made a Reasonable Application of SSI Disability Criteria" },
                    { id: 3273, title: "Composition of Disability Review Teams" },
                    { id: 3274, title: "Procedures for Making Disability Determinations" },
                    { id: 3275, title: "Coordination Between State Medicaid Agency and the SSA Disability Determination Service (DDS)" },
                    { id: 3276, title: "Referral to SSA" },
                    { id: 3277, title: "Time Limit to Determine Eligibility in Disability Cases" },
                    { id: 3280, title: "Mandatory Coordination With WIC" },
                ]
            },
            {
                id: "3300 to 3314.2",
                title: "Chapter IV - Mandatory Coverage of Categorically Needy Families and Children",
                web: {
                    url: "https://web.archive.org/web/20040808081605/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3300_to_3314.2.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910181119/http://cms.gov:80/manuals/pub45pdf/sm3300.pdf",
                    date: "1998"
                },
                zip: { date: "1998" },
                subsections: [
                    { id: 3300, title: "Introduction", },
                    { id: 3301, title: "Low Income Families With Children", },
                    { id: 3302, title: "Individuals Deemed to Be Recipients of AFDC" },
                    { id: 3303, title: "Qualified Pregnant Women" },
                    { id: 3304, title: "Qualified Children" },
                    { id: 3305, title: "Deemed Eligibility of Newborns" },
                    { id: 3306, title: "Extended Medicaid Coverage for Pregnant Women" },
                    { id: 3307, title: "Continuous Eligibility" },
                    { id: 3308, title: "Extended Medicaid Benefits to Families Who Lose AFDC Because of Earnings From Employment or Loss of Earnings Disregards" },
                    { id: 3309, title: "Qualified Family Members" },
                    { id: 3311, title: "Mandatory Coverage for Low Income Pregnant Women and Infants" },
                    { id: 3312, title: "Mandatory Coverage for Low Income Children Under Age 6" },
                    { id: 3313, title: " Mandatory Coverage for Low Income Children Under Age 19" },
                    { id: 3314, title: "Extended Medicaid Benefits to Families Who Lose Eligibility Because of Income From Support Payments" },
                ]
            },
            {
                id: 3405,
                title: "Chapter V - Mandatory Coverage of the Aged, Blind, and Disabled - Changes Due to Welfare Reform",
                web: {
                    url: "https://web.archive.org/web/20040808082505/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3405_to_3405.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910213015/http://cms.gov/manuals/pub45pdf/sm3405.pdf",
                    date: "1997"
                },
                zip: { date: "1997" },
            },
            {
                id: "3410 to 3493",
                title: "Chapter V - Mandatory Coverage of the Aged, Blind, and Disabled",
                web: {
                    url: "https://web.archive.org/web/20040808082726/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3410_to_3493.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20031127050455/http://www.cms.gov:80/manuals/pub45pdf/sm3410.pdf",
                    date: "1998"
                },
                zip: { date: "1998" },
                subsections: [
                    { id: 3410, title: "Medicaid Eligibility for Qualified Severely Impaired Individuals and Individuals in §1619 Status" },
                    { id: 3411, title: "Provisions of OBRA1986 and EODAA" },
                    { id: 3412, title: "Operational Considerations" },
                    { id: 3420, title: "Individuals in States Using More Restrictive Eligibility Requirements" },
                    { id: 3435, title: "Persons With Drug Addiction or Alcoholism" },
                    { id: 3485, title: "Coverage of Qualified Disabled and Working Individuals" },
                    { id: 3490, title: "Coverage of Qualified Medicare Beneficiaries for Medicare Cost Sharing Expenses" },
                    { id: 3491, title: "Coverage of Specified Low Income Medicare Beneficiaries for Medicare Part B Premiums" },
                    { id: 3492, title: "Coverage of Qualifying Individuals for Medicare Part B Premiums" },
                    { id: 3493, title: "Medicaid Eligibility for Disabled Children Who Lose SSI Payment" },
                ]
            },
            {
                id: "3500 to 3599.4",
                title: "Chapter VI - Optional Coverage of Categorically Needy Groups",
                web: {
                    url: "https://web.archive.org/web/20040808084030/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3500_to_3599.4.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030805123125/http://www.cms.hhs.gov:80/manuals/pub45pdf/sm3500.pdf",
                    date: "1998"
                },
                zip: { date: "1998" },
                subsections: [
                    { id: 3500, title: "Introduction" },
                    { id: 3501, title: "Definitions" },
                    { id: 3502, title: "Persons Who Meet Income and Resource Requirements for, but Do Not Receive Cash Assistance" },
                    { id: 3503, title: "Children Under Age 21" },
                    { id: 3504, title: "Reserved" },
                    { id: 3505, title: "Reserved" },
                    { id: 3506, title: "Children Under State Adoption Assistance Programs" },
                    { id: 3570, title: "Optional Presumptive Eligibility Period for Pregnant Women" },
                    { id: 3571, title: "Optional Coverage for Poor Pregnant (And Postpartum) Women, Infants and Children" },
                    { id: 3580, title: "Hospice Benefits" },
                    { id: 3581, title: "Optional Hospice Care Eligibility Group" },
                    { id: 3582, title: "Comparability of Hospice Care Benefits" },
                    { id: 3583, title: "Copayments on Hospice Care Benefits" },
                    { id: 3584, title: "Post-Eligibility Treatment of Income for Hospice Care" },
                    { id: 3589, title: "Medicaid Coverage of Home Care for Certain Disabled Children" },
                    { id: 3590, title: "Individuals Eligible for Services Under a Home and Community-Based Services Waiver" },
                    { id: 3596, title: "Optional Coverage of the Elderly and Disabled Poor for All Medicaid Benefits" },
                    { id: 3597, title: "Treatment of Couples in Medical Institutions" },
                    { id: 3598, title: "Coverage of COBRA Continuation Beneficiaries" },
                    { id: 3599, title: "Buy-In to Medicaid for the Working Disabled" },
                ]
            },
            {
                id: "3600 to 3645.6",
                title: "Chapter VII - Coverage of the Medically Needy",
                web: {
                    url: "https://web.archive.org/web/20040808070458/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3600_to_3645.6.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911083221/http://cms.gov:80/manuals/pub45pdf/sm3600.pdf",
                    date: "1997"
                },
                zip: { date: "1997" },
                subsections: [
                    { id: 3600, title: "Introduction" },
                    { id: 3601, title: "Background" },
                    { id: 3610, title: "Eligible Groups" },
                    { id: 3611, title: "Required Groups" },
                    { id: 3612, title: "Optional Eligible Groups" },
                    { id: 3613, title: "Criteria for Determining Categorically Needy and Medically Needy" },
                    { id: 3620, title: "Financial Eligibility" },
                    { id: 3621, title: "Single Income and Resource Standard" },
                    { id: 3622, title: "Cost of Living Variations" },
                    { id: 3623, title: "Defining Reasonable Standards" },
                    { id: 3624, title: "Federal Financial Participation (FFP) Limitation" },
                    { id: 3625, title: "Financial Methodologies" },
                    { id: 3626, title: "Income Eligibility" },
                    { id: 3627, title: "Budget Periods" },
                    { id: 3628, title: "Deduction of Incurred Medical and Remedial Care Expenses (Spenddown)" },
                    { id: 3630, title: "Resource Eligibility" },
                    { id: 3640, title: "Moratorium" },
                    { id: 3645, title: "Pay-In Spenddown Option" },
                ]
            },
            {
                id: "3700 to 3714.2",
                title: "Chapter VIII - Post-Eligibility",
                web: {
                    url: "https://web.archive.org/web/20040808074001/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3700_to_3714.2.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20050524160719/http://www.cms.hhs.gov:80/manuals/pub45pdf/sm3700.pdf",
                    date: "1998"
                },
                zip: { date: "1998" },
                subsections: [
                    { id: 3700, title: "Introduction" },
                    { id: 3701, title: "General Statement of Post-Eligibility Process" },
                    { id: 3702, title: "Deductions From the Individual's Total Income" },
                    { id: 3703, title: "Required Deductions" },
                    { id: 3704, title: "Optional Deductions" },
                    { id: 3705, title: "Post-Eligibility Treatment of Certain Payments Made by the Department of Veterans Affairs" },
                    { id: 3708, title: "Post-Eligibility Treatment of Certain Disabled Institutionalized Individuals" },
                    { id: 3710, title: "Special Post-Eligibility Process for Institutionalized Persons With Community Spouses" },
                    { id: 3711, title: "Income Used in the Post-Eligibility Process" },
                    { id: 3712, title: "Mandatory Deductions From Income" },
                    { id: 3713, title: "Monthly Income Allowances for Community Spouses and Other Family Members" },
                    { id: 3714, title: "Notice, Hearings and Appeals" },
                ]
            },
            {
                id: "3800 to 3812",
                title: "Chapter IX - Financial Eligibility Requirements and Options",
                zip: {
                    date: "1994 and 2001"
                },
                web: {
                    url: "https://web.archive.org/web/20040808074529/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3800_to_3812.asp",
                    date: "2001"
                },
                pdf: {
                    url: "https://web.archive.org/web/20031201073207/http://www.cms.gov/manuals/pub45pdf/sm3800.pdf",
                    date: "2001"
                },
                subsections: [
                    { id: 3810, title: "Medicaid Estate Recoveries" },
                    { id: 3812, title: "Treatment of Contributions From Relatives to Medicaid Applicants or Recipients" },
                ]
            },
            {
                id: "3900 to 3910.15",
                title: "Chapter X - Third Party Liability",
                zip: {
                    date: "2015"
                },
                web: {
                    url: "https://web.archive.org/web/20040808075451/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3900_to_3910.15.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20050308152122/http://www.cms.hhs.gov:80/manuals/pub45pdf/sm3900.pdf",
                    date: "1998"
                },
                subsections: [
                    { id: 3900, title: "Third Party Liability (TPL)" },
                    { id: 3901, title: "Definitions" },
                    { id: 3902, title: "General TPL Requirements" },
                    { id: 3903, title: "Identification of Resources (42 CFR 433.138)" },
                    { id: 3904, title: "Payment of Claims (42 CFR 433.139)" },
                    { id: 3905, title: "Assignment of Rights to Benefits - (42 CFR 433.145)" },
                    { id: 3906, title: "Cooperative Agreements and Incentive Payments" },
                    { id: 3907, title: "Distribution of Collections" },
                    { id: 3908, title: "Conflicting Claims by Medicare and Medicaid" },
                    { id: 3909, title: "Medicare/Medicaid Crossover Claims" },
                    { id: 3910, title: "Medicaid Payments for Recipients Under Group Health Plans" },
                ]
            },
            {
                id: "IM 3570",
                title: "Requirements for Eligibility Under a Special Income Level",
                zip: {
                    date: "1986"
                },
                web: {
                    url: "https://web.archive.org/web/20040227225635/http://www.cms.hhs.gov/manuals/45_smm/sm_03_im_3570.asp",
                    date: "1986"
                },
                pdf: { date: "unavailable" },
            },
            {
                id: "IM 3900",
                title: "Third Party Liability (TPL)",
                zip: {
                    date: "1994"
                },
                web: {
                    url: "https://web.archive.org/web/20040808080724/http://www.cms.hhs.gov/manuals/45_smm/sm_03_im_3900_to_im_3900.asp",
                    date: "1994"
                },
                pdf: { date: "unavailable" },
            },
        ],
    },
    {
        id: 4,
        title: "Part 4 – Services",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_04.zip",
            date: "2015"
        },
        web: {
            url: "https://web.archive.org/web/20041212082209/http://www.cms.hhs.gov/manuals/45_smm/SM_04_4_toc.asp",
            date: "1999"
        },
        subsections: [
            {
                id: "4130 to 4253",
                title: "Requirements and Limits Applicable to All Services; Requirements and Limits Applicable to Specific Services",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041206171539/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4130_to_4253.asp",
                    date: "1990"
                },
                pdf: {
                    url: "https://web.archive.org/web/20050110002858/http://cms.hhs.gov:80/manuals/pub45pdf/sm4130.pdf",
                    date: "1990"
                },
                subsections: [
                    { id: 4130, title: "Comparability of Services" },
                    { id: 4201, title: "Organ Transplants" },
                    { id: 4221, title: "Outpatient Psychiatric Services." },
                    { id: 4231, title: "Federally Qualified Health Center (FQHC) and Other Ambulatory Services" },
                    { id: 4250, title: "Minimum Federal Criteria for States to Use in Making Preadmission and Annual Review Determinations About Admission to or Continued Residence in Nursing Facilities for Individuals Who Have Mental Illness or Mental Retardation" },
                    { id: 4251, title: "Minimum Evaluation Criteria Specific to Screening Persons With MR or MI for the Need for NF Level of Services (PASARR/NF)" },
                    { id: 4252, title: "Minimum Criteria Specific to the Screening of Persons With MI (PASARR/MI)" },
                    { id: 4253, title: "Minimum Criteria Specific to the Screening for Persons With MR (PASARR/MR)" },
                ]
            },
            {
                id: "4270 to 4390.1",
                title: "Requirements and Limits Applicable to Specific Services",
                zip: { date: 2015 },
                web: {
                    url: "https://web.archive.org/web/20041206172221/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4270_to_4390.1.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20040503210948/http://cms.hhs.gov:80/manuals/pub45pdf/sm4270.pdf",
                    date: "1997"
                },
                subsections: [
                    { id: 4270, title: "Family Planning Services" },
                    { id: 4280, title: "Establishment and Use of Medicaid Unique Physician Identifier" },
                    { id: 4281, title: "Restriction on Payments for Physician Services" },
                    { id: 4282, title: "Maintenance of List of Physicians by States" },
                    { id: 4283, title: "Conditions for Foreign Medical Graduate Certification" },
                    { id: 4301, title: "Home Respiratory Care for Ventilator-Dependent Individuals" },
                    { id: 4302, title: "Optional Targeted Case Management Services - Basis, Scope and Purpose" },
                    { id: 4305, title: "Hospice Services" },
                    { id: 4306, title: "Hospice Reimbursement" },
                    { id: 4307, title: "Payment for Physician Services Under Hospice" },
                    { id: 4308, title: "Optional Cap on Overall Hospice Reimbursement" },
                    { id: 4310, title: "Private Duty Nursing Services" },
                    { id: 4320, title: "Clinic Services." },
                    { id: 4370, title: "Less Than Effective and Identical, Related or Similar Drugs" },
                    { id: 4375, title: "Tuberculosis Related Services" },
                    { id: 4385, title: "Preventive Services" },
                    { id: 4390, title: "Institutions for Mental Diseases" },
                ]
            },
            {
                id: "4395 to 4435.4",
                title: "Requirements and Limits Applicable to Specific Services",
                zip: { date: 1995 },
                web: {
                    url: "https://web.archive.org/web/20041206172723/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4395_to_4435.4.asp",
                    date: "1995"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911004440/http://cms.gov:80/manuals/pub45pdf/sm4395.pdf",
                    date: "1995"
                },
                subsections: [
                    { id: 4395, title: "Inappropriate Placement of Mentally Retarded Persons in SNFs and ICFs" },
                    { id: 4396, title: "Application of the Educational Services Exclusion in ICFs/MR" },
                    { id: 4397, title: "Application of the Vocational Services Exclusion in ICFs/MR" },
                    { id: 4398, title: "Persons With Related Conditions" },
                    { id: 4415, title: "Nurse Practitioner Services" },
                    { id: 4420, title: "Nurse-Midwife Services" },
                    { id: 4421, title: "Services for Pregnant Women" },
                    { id: 4430, title: "Legal Background and Authority" },
                    { id: 4431, title: "Federal Funding of Abortions" },
                    { id: 4432, title: "Federal Funding of Abortion Related Services" },
                    { id: 4434, title: "Legal Background and Authority" },
                    { id: 4435, title: "Sterilization by Hysterectomy" },
                ]
            },
            {
                id: "4440 to 4444",
                title: "Requirements and Limits Applicable to Specific Services",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041206161214/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4440_to_4444.asp",
                    date: "1998"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911050125/http://cms.gov:80/manuals/pub45pdf/sm4440.pdf",
                    date: "1997"
                },
                subsections: [
                    { id: 4440, title: "Home and Community-Based Services - Basis, Scope, and Purpose" },
                    { id: 4441, title: "Home and Community-Based Services - Process" },
                    { id: 4442, title: "Waiver Request Requirements" },
                    { id: 4443, title: "Home and Community-Based Services - Model Waiver Request" },
                    { id: 4444, title: "Home and Community-Based Services - Procedures to Request" },
                ]
            },
            {
                id: "4444 to 4658",
                title: "Requirements and Limits Applicable to Specific Services",
                zip: { date: 1999 },
                web: {
                    url: "https://web.archive.org/web/20041206161854/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4444_to_4658.asp",
                    date: "1999"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911080158/http://cms.gov:80/manuals/pub45pdf/sm4444.pdf",
                    date: "1999"
                },
                subsections: [
                    { id: "4444 (Continued)", title: "Home and Community-Based Services - Procedures to Request" },
                    { id: 4445, title: "Home and Community-Based Services Amendments" },
                    { id: 4446, title: "Home and Community-Based Services Terminations" },
                    { id: 4460, title: "Nurse Aide Registry" },
                    { id: 4470, title: "Specification of Resident Assessment Instruments for Use in Long Term Care Facilities" },
                    { id: 4480, title: "Personal Care Services" },
                    { id: 4560, title: "Skilled Nursing Facility (SSF) and Intermediate Care Facility (ICF) Services Provided by Swing Bed Hospitals" },
                    { id: 4570, title: "Ambulatory Surgical Center Services." },
                    { id: 4580, title: "Phlebotomy and Case Management Services Associated With the Drug Clozaril" },
                    { id: 4600, title: "Usage of Certification Transmittal, HCFA-1539" },
                    { id: 4601, title: "Usage of the Statement of Deficiencies and Plan of Correction, HCFA-2567" },
                    { id: 4602, title: "Provider Agreements" },
                    { id: 4603, title: "Readmission to the Medicare or Medicaid Program After Termination" },
                    { id: 4604, title: "Authority to Grant Life Safety Code Waivers for Medicaid Only NFs" },
                    { id: 4650, title: "Termination - General" },
                    { id: 4651, title: "Basis for Terminating Program Participation" },
                    { id: 4652, title: "Termination Procedures--Immediate and Serious Threat to Patient Health and Safety" },
                    { id: 4653, title: "Termination Procedures--Noncompliance Limits Capacity of Facility to Furnish Adequate Level or Quality of Care - No Immediate and Serious Threat to Health and Safety" },
                    { id: 4654, title: "Nonrenewal or Cancellation of Time Limited Agreements for Long Term Care Facilities (Medicare and Medicaid)" },
                    { id: 4655, title: "Notice of Termination" },
                    { id: 4656, title: "Additional Communications With Facility" },
                    { id: 4657, title: "Relocating Patients or Residents Displaced by Termination or Closure" },
                    { id: 4658, title: "Guidance to States for Medicaid Nursing Facility (NF) Remedies" },
                ]
            },
            {
                id: "Addendum A",
                title: "Wage Indices for Urban Areas",
                zip: { date: 1987 },
                web: {
                    url: "https://web.archive.org/web/20041206162508/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_add_a.asp",
                    date: "1987"
                },
                pdf: { date: "unavailable" },
            },
            {
                id: "Addendum B",
                title: "Wage Indices for Rural Areas",
                zip: { date: 1987 },
                web: {
                    url: "https://web.archive.org/web/20041206163143/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_add_b.asp",
                    date: "1987"
                },
                pdf: { date: "unavailable" },
            },
            {
                id: "IM 4604",
                title: "Change in Authority to Grant Life Safety Code Waivers for Medicaid Only NFs",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041206164106/http://www.cms.hhs.gov/manuals/45_smm/sm_04_im_4604.asp",
                    date: "1991"
                },
                pdf: { date: "unavailable" },
            },
        ],
    },
    {
        id: 5,
        title: "Part 5 – Early and Periodic Screening",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_05.zip",
            date: "1998"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222101/http://www.cms.hhs.gov/manuals/pub45pdf/smm5t.pdf",
            date: "1998"
        },
        web: {
            url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp",
            date: "1998"
        },
        subsections: [
            {
                id: 5010,
                title: "Introduction - Overview",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454938",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5110,
                title: "Program Requirements and Methods - Basic Requirements",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454939",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5121,
                title: "Program Requirements and Methods - Informing Families of EPSDT Services",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454940",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5122,
                title: "Program Requirements and Methods - EPSDT Service Requirements",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454941",
                    date: 1994
                },
                pdf: { date: 1994 },
            },
            {
                id: 5123,
                title: "Program Requirements and Methods - Screening Service Delivery and Content",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454942",
                    date: 1998
                },
                pdf: { date: 1998 },
            },
            {
                id: 5124,
                title: "Program Requirements and Methods - Diagnosis and Treatment",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454946",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5140,
                title: "Program Requirements and Methods - Periodicity Schedule",
                zip: { date: 1995 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454947",
                    date: 1995
                },
                pdf: { date: 1995 },
            },
            {
                id: 5150,
                title: "Program Requirements and Methods - Transportation and Scheduling Assistance (Support Services)",
                zip: { date: 1995 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454948",
                    date: 1995
                },
                pdf: { date: 1995 },
            },
            {
                id: 5220,
                title: "Utilization of Providers and Coordination With Related Programs - Utilization of Providers",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454949",
                    date: 1994
                },
                pdf: { date: 1994 },
            },
            {
                id: 5230,
                title: "Utilization of Providers and Coordination With Related Programs - Coordination With Related Agencies and Programs",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454950",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5240,
                title: "Utilization of Providers and Coordination With Related Programs - Continuing Care",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454951",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5310,
                title: "Administration - Program Monitoring, Planning, and Evaluation",
                zip: { date: 1995 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454952",
                    date: 1995
                },
                pdf: { date: 1995 },
            },
            {
                id: 5320,
                title: "Administration - Information Needs and Reporting",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454953",
                    date: 1994
                },
                pdf: { date: 1994 },
            },
            {
                id: 5330,
                title: "Administration - Timeliness",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454956",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 5340,
                title: "Administration - Reimbursement",
                zip: { date: 1995 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454957",
                    date: 1995
                },
                pdf: { date: 1995 },
            },
            {
                id: 5350,
                title: "Administration - Confidentiality",
                zip: { date: 1993 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454958",
                    date: 1993
                },
                pdf: { date: 1993 },
            },
            {
                id: 5360,
                title: "Administration - Annual Participation Goals",
                zip: { date: 1993 },
                web: {
                    url: "https://web.archive.org/web/20041106183904/http://www.cms.hhs.gov/manuals/45_smm/sm_05_5_5010_to_5360with_toc.asp#_toc490454959",
                    date: 1993
                },
                pdf: { date: 1993 },
            },
        ],
    },
    {
        id: 6,
        title: "Part 6 – Payments for Services",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_06.zip",
            date: "2000"
        },
        pdf: {
            url: "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/smm6t.pdf",
            date: "2000"
        },
        web: {
            url: "https://web.archive.org/web/20041212235830/http://www.cms.hhs.gov/manuals/45_smm/sm_06_6_toc.asp",
            date: "2000"
        },
        subsections: [
            {
                id: "6000 to 6400.3",
                title: "",
                zip: { date: 1997 },
                web: {
                    url: "https://web.archive.org/web/20041118085615/http://www.cms.hhs.gov/manuals/45_smm/sm_06_6000_to_6400.3.asp",
                    date: 1997
                },
                pdf: { date: 1997 },
                subsections: [
                    { id: 6000, title: "Inpatient Hospital and Long-Term Care Reimbursement - General", },
                    { id: 6001, title: "Statutory Requirements", },
                    { id: 6002, title: "Requirements Necessary for State Plan Sections 4.19(A) or 4.19(D)", },
                    { id: 6003, title: "HCFA Action", },
                    { id: 6004, title: "Public Notice", },
                    { id: 6005, title: "Upper Payment Limit Requirements", },
                    { id: 6006, title: "Appeals", },
                    { id: 6300, title: "Payment for Outpatient Clinical Diagnostic Laboratory Tests for Calendar Quarters Beginning on or After October 1, 1984", },
                    { id: 6301, title: "Rural Health Clinic Reimbursement", },
                    { id: 6302, title: "Rural Health Clinic Carriers", },
                    { id: 6303, title: "Federally Qualified Health Center and Other Ambulatory Services Payment", },
                    { id: 6305, title: "Specific Upper Limits for Multiple Source and \"Other\" Drugs", },
                    { id: 6320, title: "Direct Reimbursement by States to Medicaid Recipients to Correct Erroneous Denials", },
                    { id: 6400, title: "Payment for Physician Services to Pregnant Women and Children", },
                ]
            },
            {
                id: "Addendum A",
                title: "",
                zip: { date: 2000 },
                web: {
                    url: "https://web.archive.org/web/20041213115707/http://www.cms.hhs.gov/manuals/45_smm/sm_06_6000_ad_a.asp",
                    date: 2000
                },
                pdf: { date: 2000 },
            },
            {
                id: "IM 6000 to 6000.5",
                title: "Inpatient Hospital and Long-Term Care Reimbursement",
                zip: { date: 1988 },
                web: {
                    url: "https://web.archive.org/web/20041212235830/http://www.cms.hhs.gov/manuals/45_smm/sm_06_im_6000_to_6000.5.asp",
                    date: 1988
                },
                pdf: { date: 1988 },
            },
            {
                id: "IM 6007",
                title: "Revaluation of Assets",
                zip: { date: 1984 },
                web: {
                    url: "https://web.archive.org/web/20041213121344/http://www.cms.hhs.gov/manuals/45_smm/sm_06_im_6007_to_6007.asp",
                    date: 1984
                },
                pdf: { date: 1984 },
            },
        ],
    },
    {
        id: 7,
        title: "Part 7 – Quality Control",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_07.zip",
            date: "1994"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222046/http://www.cms.hhs.gov/manuals/pub45pdf/smm7t.pdf",
            date: "1994"
        },
        web: {
            url: "https://web.archive.org/web/20041205032506/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7_toc.asp",
            date: "1994"
        },
        subsections: [
            {
                id: "",
                title: "Legal Background and Authority",
                zip: { date: "no date" },
                web: { date: "unavailable" },
                pdf: { date: "no date" },
            },
            {
                id: "7000 to 7099",
                title: "Chapter 1 - Administration and Objectives",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041209184841/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7000_to_7099.asp",
                    date: 1992
                },
                pdf: { date: 1992 },
                subsections: [
                    { id: 7000, title: "Introduction", },
                    { id: 7005, title: "Administration of MEQC", },
                    { id: 7015, title: "Federal MEQC State Plan Requirements", },
                    { id: 7030, title: "Components of the MEQC System", },
                    { id: 7031, title: "Sample Selection", },
                    { id: 7032, title: "Review Process", },
                    { id: 7033, title: "Individual Corrective Action", },
                    { id: 7034, title: "Data Management", },
                    { id: 7035, title: "Error Analysis", },
                    { id: 7036, title: "Dissemination of Findings", },
                    { id: 7050, title: "MEQC and Corrective Action", },
                    { id: 7052, title: "MEQC Cap Requirements", },
                    { id: 7055, title: "MEQC Cap Format", },
                    { id: 7099, title: "Role of a State Model System in the Evaluation Process", },
                ]
            },
            {
                id: "7100 to 7124",
                title: "Chapter 2 - Sampling Methods",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041205015137/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7100_to_7124.asp",
                    date: 1992
                },
                pdf: { date: 1992 },
                subsections: [
                    { id: 7100, title: "Quality Control Sampling", },
                    { id: 7102, title: "Overview of the MEQC System", },
                    { id: 7104, title: "MEQC Sampling Requirements", },
                    { id: 7109, title: "Types of Errors", },
                    { id: 7110, title: "Validity and Reliability of Statistical Data", },
                    { id: 7113, title: "Stratification", },
                    { id: 7120, title: "General Sampling Requirements of MEQC", },
                    { id: 7121, title: "Sample Unit", },
                    { id: 7122, title: "Sample Sizes", },
                    { id: 7123, title: "Populations to Be Sampled", },
                    { id: 7124, title: "Sampling Frames", },
                ]
            },
            {
                id: "7125 to 7154",
                title: "Chapter 2 - Sampling Methods",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041205030649/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7125_to_7154.asp",
                    date: 1992
                },
                pdf: { date: 1992 },
                subsections: [
                    { id: 7125, title: "Sample Selection", },
                    { id: 7126, title: "Claims Collection", },
                    { id: 7130, title: "Requirements for Sampling Plan Documentation", },
                    { id: 7132, title: "Random Sample Selection Procedures", },
                    { id: 7133, title: "Calculation of Sampling Interval", },
                    { id: 7134, title: "Selection of Cases for the Review Month", },
                    { id: 7140, title: "Procedures for Correcting the Monthly Sample for Excessive Oversampling and Undersampling", },
                    { id: 7142, title: "Correcting for Excessive Oversampling", },
                    { id: 7144, title: "Correcting for Undersampling", },
                    { id: 7146, title: "Alternate Method of Correcting for Undersampling or Oversampling", },
                    { id: 7150, title: "Guidelines for Expanded and Substratified Samples", },
                    { id: 7152, title: "Guidelines for Expanding Sample Size", },
                    { id: 7154, title: "Guidelines for Further Stratification", },
                ]
            },
            {
                id: 7199,
                title: "Chapter 2 - Sampling Methods - Exhibits",
                zip: { date: 1989 },
                web: {
                    url: "https://web.archive.org/web/20041209205013/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7199_to_exhibit_2.asp",
                    date: 1989
                },
                pdf: { date: 1989 },
            },
            {
                id: "Appendix A",
                title: "Chapter 2 - Sampling Methods - Glossary of Terms; MEQC Error Rate Calculation",
                zip: { date: 1993 },
                web: {
                    url: "https://web.archive.org/web/20041205013851/http://www.cms.hhs.gov/manuals/45%5Fsmm/sm%5F07%5F7199%5Fapa.asp",
                    date: "1993"
                },
                pdf: { date: 1993 },
            },
            {
                id: "Appendix B",
                title: "Chapter 2 - Sampling Methods - Criteria for Adjusting Anticipated Error Rates Pursuant to 42 CFR 431.865(d)",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041209185620/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7199_apb.asp",
                    date: 1992
                },
                pdf: { date: 1992 },
            },
            {
                id: "Appendix C",
                title: "Chapter 2 - Sampling Methods - Retrospective Sampling",
                zip: { date: "no date" },
                web: {
                    url: "https://web.archive.org/web/20041209204006/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7199_apc.asp",
                    date: "no date"
                },
                pdf: { date: "no date" },
            },
            {
                id: "7200 to 7230",
                title: "Chapter 3 - Review Process",
                zip: { date: 1993 },
                web: {
                    url: "https://web.archive.org/web/20041209210243/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7200_to_7230.asp",
                    date: 1993
                },
                pdf: { date: 1993 },
                subsections: [
                    { id: 7200, title: "Medicaid Eligibility Overview", },
                    { id: 7203, title: "Definitions of Key Terms", },
                    { id: 7206, title: "Medicaid Eligibility Quality Control (MEQC) Review", },
                    { id: 7209, title: "Scope of MEQC System", },
                    { id: 7212, title: "MEQC Operation", },
                    { id: 7215, title: "Role of Reviewer", },
                    { id: 7218, title: "Independence of MEQC Review", },
                    { id: 7221, title: "Documentation of Reviews", },
                    { id: 7224, title: "Approach to MEQC", },
                    { id: 7227, title: "Cases to Be Reviewed", },
                    { id: 7230, title: "Cases Which Are Not Reviewed", },
                ]
            },
            {
                id: "7233 to 7265",
                title: "Chapter 3 - Review Process",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041205032506/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7233_to_7265.asp",
                    date: 1994
                },
                pdf: { date: 1994 },
                subsections: [
                    { id: 7233, title: "Cash Assistance Eligibility Determinations", },
                    { id: 7236, title: "Review of AFDC Cash Cases/Individuals", },
                    { id: 7237, title: "Review of AFDC-Related and SSI-Related Cases", },
                    { id: 7239, title: "Review of SSI Cash Cases Under §1903(u) of the Act Enacted by TEFRA 1982", },
                    { id: 7242, title: "Review of SSI Cash Cases in SSI-Criteria and 209(b) States", },
                    { id: 7245, title: "Review of Aged, Blind and Disabled Cases in 209(b) States and United States Territories", },
                    { id: 7248, title: "Case Record Review", },
                    { id: 7251, title: "Field Investigation", },
                    { id: 7254, title: "In-Person Interview", },
                    { id: 7257, title: "Collateral Contacts", },
                    { id: 7260, title: "Worksheet for Integrated AFDC, Adult, Food Stamp, and Medicaid Eligibility Quality Control Reviews (Facesheet)", },
                    { id: 7263, title: "Elements of Eligibility and Payment Determination (Integrated QC Worksheet)", },
                    { id: 7264, title: "Mandatory Use of Ievs Information", },
                    { id: 7265, title: "Hold Harmless Provision of Immigration Reform and Control Act (IRCA)", },
                ]
            },
            {
                id: "7265.1 to 7272",
                title: "Chapter 3 - Review Process",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041209212827/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7265.1_to_7269.5.asp",
                    date: 1994
                },
                pdf: { date: 1994 },
                subsections: [
                    { id: 7265, title: "Hold Harmless Provision of Immigration Reform and Control Act (IRCA)", },
                    { id: 7266, title: "Documentation", },
                    { id: 7269, title: "Verification Standards", },
                    { id: 7272, title: "Verification Guide", },
                ]
            },
            {
                id: "7272 (Continued)",
                title: "Chapter 3 - Review Process - Verification Guide",
                zip: { date: 1994 },
                web: {
                    url: "https://web.archive.org/web/20041210111723/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7272_to_7272.asp",
                    date: 1994
                },
                pdf: { date: 1994 },
            },
            {
                id: "7275 to 7355",
                title: "Chapter 3 - Review Process",
                zip: { date: 1993 },
                web: {
                    url: "https://web.archive.org/web/20041209213227/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7275_to_7355.asp",
                    date: 1993
                },
                pdf: { date: 1993 },
                subsections: [
                    { id: 7275, title: "Instructions for Integrated Review Schedule (IRS) - Form HCFA 301", },
                    { id: 7278, title: "Administrative Period", },
                    { id: 7300, title: "Classification of Errors", },
                    { id: 7303, title: "Eligibility Errors", },
                    { id: 7306, title: "Reporting of Eligibility Errors", },
                    { id: 7309, title: "Technical Errors", },
                    { id: 7310, title: "Hierarchy of MEQC Errors", },
                    { id: 7312, title: "Eligible With Ineligible Services", },
                    { id: 7315, title: "Erroneous Payment Computation", },
                    { id: 7316, title: "Dollar Amount of Case Eligibility Errors", },
                    { id: 7318, title: "Computation of Liability Errors", },
                    { id: 7319, title: "Review Month Income Projected Forward Throughout Spenddown Period", },
                    { id: 7321, title: "Identification of Claims for Services", },
                    { id: 7324, title: "Rounding to Nearest Dollar", },
                    { id: 7327, title: "Determining Final Misspent Dollar Amounts of Cases Containing Initial Eligibility Errors", },
                    { id: 7330, title: "Determining Final Misspent Dollar Amounts of Cases Containing Initial Liability Understated Errors", },
                    { id: 7333, title: "Determining Final Misspent Dollar Amounts of Institutional Cases", },
                    { id: 7336, title: "Identifying the Primary Eligibility and Liability Errors", },
                    { id: 7339, title: "Definition of Misspent Dollar Amounts for Cases Containing Final Eligibility or Liability Errors", },
                    { id: 7342, title: "Completing the Unduplicated Dollar Error Amount Worksheet (Optional)", },
                    { id: 7343, title: "Computation of Error Amounts for Cases Involving Beneficiaries Dually Eligible for QMB and Non-QMB Coverage Group", },
                    { id: 7275, title: "Instructions for Integrated Review Schedule (IRS) - Form HCFA 301", },
                    { id: 7278, title: "Administrative Period", },
                    { id: 7300, title: "Classification of Errors", },
                    { id: 7303, title: "Eligibility Errors", },
                    { id: 7306, title: "Reporting of Eligibility Errors", },
                    { id: 7309, title: "Technical Errors", },
                    { id: 7310, title: "Hierarchy of MEQC Errors", },
                    { id: 7312, title: "Eligible With Ineligible Services", },
                    { id: 7315, title: "Erroneous Payment Computation", },
                    { id: 7316, title: "Dollar Amount of Case Eligibility Errors", },
                    { id: 7318, title: "Computation of Liability Errors", },
                    { id: 7319, title: "Review Month Income Projected Forward Throughout Spenddown Period", },
                    { id: 7321, title: "Identification of Claims for Services", },
                    { id: 7324, title: "Rounding to Nearest Dollar", },
                    { id: 7327, title: "Determining Final Misspent Dollar Amounts of Cases Containing Initial Eligibility Errors", },
                    { id: 7330, title: "Determining Final Misspent Dollar Amounts of Cases Containing Initial Liability Understated Errors", },
                    { id: 7333, title: "Determining Final Misspent Dollar Amounts of Institutional Cases", },
                    { id: 7336, title: "Identifying the Primary Eligibility and Liability Errors", },
                    { id: 7339, title: "Definition of Misspent Dollar Amounts for Cases Containing Final Eligibility or Liability Errors", },
                    { id: 7342, title: "Completing the Unduplicated Dollar Error Amount Worksheet (Optional)", },
                    { id: 7343, title: "Computation of Error Amounts for Cases Involving Beneficiaries Dually Eligible for QMB and Non-QMB Coverage Group", },
                    { id: 7350, title: "Federal Monitoring", },
                    { id: 7355, title: "Record Maintenance", },
                ]
            },
            {
                id: "7500 to 7599",
                title: "Chapter 4 - Reports",
                zip: { date: 1992 },
                web: {
                    url: "https://web.archive.org/web/20041205032506/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7500_to_7599.asp",
                    date: 1992
                },
                pdf: { date: 1992 },
                subsections: [
                    { id: 7500, title: "Introduction", },
                    { id: 7505, title: "Analysis of Reported Data", },
                    { id: 7510, title: "Instructions", },
                    { id: 7520, title: "Table Instructions - Table V", },
                ]
            },
            {
                id: "7700 to 7770.2",
                title: "Chapter 8 - Quality Control of Negative Case Actions",
                zip: { date: 1994 },
                web: { date: "unavailable" },
                pdf: { date: "unavailable" },
            },
        ],
    },
    {
        id: 8,
        title: "Part 8 – Program Integrity",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_08.zip",
            date: "1983"
        },
        web: {
            url: "https://web.archive.org/web/20041118225622/http://www.cms.hhs.gov/manuals/45_smm/sm_08_8_8001_to_8003with_toc.asp",
            date: "1983"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106221935/http://www.cms.hhs.gov/manuals/pub45pdf/smm8t.pdf",
            date: "1983"
        },
        subsections: [
            {
                id: 8001,
                title: "Disclosure of Information by Providers and Fiscal Agents - Claims for Payment in Alcohol and Drug Abuse Case - General",
                zip: { date: 1983 },
                web: {
                    url: "https://web.archive.org/web/20041118225622/http://www.cms.hhs.gov/manuals/45_smm/sm_08_8_8001_to_8003with_toc.asp#_toc490446506",
                    date: 1983
                },
                pdf: { date: 1983 },
            },
            {
                id: 8002,
                title: "Disclosure of Information by Providers and Fiscal Agents - Confidentiality of Provider Records",
                zip: { date: 1983 },
                web: {
                    url: "https://web.archive.org/web/20041118225622/http://www.cms.hhs.gov/manuals/45_smm/sm_08_8_8001_to_8003with_toc.asp#_toc490446507",
                    date: 1983
                },
                pdf: { date: 1983 },
            },
            {
                id: 8003,
                title: "Disclosure of Information by Providers and Fiscal Agents - Consent Form",
                zip: { date: 1983 },
                web: {
                    url: "https://web.archive.org/web/20041118225622/http://www.cms.hhs.gov/manuals/45_smm/sm_08_8_8001_to_8003with_toc.asp#_toc490446508",
                    date: 1983
                },
                pdf: { date: 1983 },
            },
        ],
    },
    {
        id: 9,
        title: "Part 9 – Utilization Control",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_09.zip",
            date: "1989"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222347/http://www.cms.hhs.gov/manuals/pub45pdf/smm9t.pdf",
            date: "1989"
        },
        web: {
            url: "https://web.archive.org/web/20041212235359/http://www.cms.hhs.gov/manuals/45_smm/sm_09_9_toc.asp",
            date: "1989"
        },
        subsections: [
            {
                id: "9100 to 9180.3, Exhibits 1 to 6",
                title: "General Provisions",
                zip: { date: 1988 },
                web: {
                    url: "https://web.archive.org/web/20041213121705/http://www.cms.hhs.gov/manuals/45_smm/sm_09_9100_to_exhibit_6.asp",
                    date: 1988
                },
                pdf: { date: 1988 },
                subsections: [
                    { id: 9100, title: "Legal Background and Authority for the Utilization Control Program", },
                    { id: 9102, title: "Scope of the UC Quality Review System", },
                    { id: 9105, title: "Requirements for Content of Quarterly Showings", },
                    { id: 9110, title: "Completing Facility Lists", },
                    { id: 9111, title: "Facilities for Which No Reviews Were Performed", },
                    { id: 9115, title: "Submission of Quarterly Showings", },
                    { id: 9120, title: "Acceptable Reasons for Not Meeting Annual Review Requirements of the Quarterly Showing", },
                    { id: 9125, title: "Procedures When a State Claims an Exception Clause", },
                    { id: 9130, title: "Recipients in Out-of-State Facilities", },
                    { id: 9135, title: "Recipients in Facilities Without Valid Provider Agreements", },
                    { id: 9140, title: "Validation Survey in the State Agency", },
                    { id: 9150, title: "Conditions for Meeting a 100-Percent Recipient Review", },
                    { id: 9155, title: "A Reasonable State System for Identifying Recipients for Review", },
                    { id: 9160, title: "Multiple IOC Reviews", },
                    { id: 9165, title: "Acceptable Reasons for Not Meeting Requirements for a 100 Percent Recipient Review", },
                    { id: 9170, title: "Entrance and Exit Conferences", },
                    { id: 9180, title: "Reductions in Federal Financial Participation", },
                    { id: "Exhibit 1", title: "", },
                    { id: "Exhibit 2", title: "", },
                    { id: "Exhibit 3", title: "", },
                    { id: "Exhibit 4", title: "", },
                    { id: "Exhibit 5", title: "", },
                    { id: "Exhibit 6", title: "", },
                ]
            },
            {
                id: 9214,
                title: "Physician Certification/Recertification - Legal Background",
                zip: { date: "no date" },
                web: {
                    url: "https://web.archive.org/web/20041212235359/http://www.cms.hhs.gov/manuals/45_smm/sm_09_9214.asp",
                    date: "no date"
                },
                pdf: { date: "no date" },
            },
            {
                id: "9215 to 9350",
                title: "Physician Certification/Recertification; Superior UR Systems",
                zip: { date: 1986 },
                web: {
                    url: "https://web.archive.org/web/20041212235359/http://www.cms.hhs.gov/manuals/45_smm/sm_09_9215_to_9350.asp",
                    date: 1986
                },
                pdf: { date: "unavailable" },
                subsections: [
                    { id: 9215, title: "Certification", },
                    { id: 9216, title: "Plan of Care Requirements", },
                    { id: 9220, title: "Recertification", },
                    { id: 9300, title: "Submitting Superior UR System Waiver Request to HCFA", },
                    { id: 9310, title: "Utilization Review Features Which Will Not Be Waived", },
                    { id: 9320, title: "Content of Initial Waiver Request", },
                    { id: 9330, title: "Content of Renewal of Waiver Request", },
                    { id: 9340, title: "Decisions and Notifications by HCFA", },
                    { id: 9350, title: "Withdrawal of HCFA Approval", },
                ]
            },
            {
                id: "IM 9215 to IM 9216",
                title: "",
                zip: { date: 1989 },
                web: {
                    url: "https://web.archive.org/web/20041213115942/http://www.cms.hhs.gov/manuals/45_smm/sm_09_im_9215.asp",
                    date: 1989
                },
                pdf: { date: 1989 },
                subsections: [
                    {
                        id: "IM 9215",
                        title: "Certification of the Need for Inpatient SNF or ICF Care",
                    },
                    {
                        id: "IM 9216",
                        title: "Who May Establish a Plan of Care for SNF or ICF Inpatients",
                    },
                ]
            },
            {
                id: "IM 9220",
                title: "Recertification of the Need for Inpatient SNF or ICF Care",
                zip: { date: 1989 },
                web: {
                    url: "https://web.archive.org/web/20041213112941/http://www.cms.hhs.gov/manuals/45_smm/sm_09_im_9220.asp",
                    date: 1989
                },
                pdf: { date: 1989 },
            },
        ],
    },
    {
        id: 11,
        title: "Part 11 – Medicaid Management Information System",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_11.zip",
            date: "2015"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222214/http://www.cms.hhs.gov/manuals/pub45pdf/smm11t.pdf",
            date: "1998"
        },
        web: {
            url: "https://web.archive.org/web/20041212235810/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11_toc.asp",
            date: "1998"
        },
        subsections: [
            {
                id: "11000 to 11115",
                title: "Chapter 1 - General",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041213114014/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11100_to_11115.asp",
                    date: 1998
                },
                pdf: { date: 1998 },
                subsections: [
                    { id: 11100, title: "Background", },
                    { id: 11105, title: "Introduction", },
                    { id: 11110, title: "Definitions", },
                    { id: 11115, title: "Objectives", },
                ]
            },
            {
                id: "11200 to 11260",
                title: "Chapter 2 - Approval of MMIS Systems",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041213114442/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11200_to_11260.asp",
                    date: 1998
                },
                pdf: { date: 1998 },
                subsections: [
                    { id: 11200, title: "Applicable Federal Approval Requirements", },
                    { id: 11205, title: "90 Percent FFP - General Regulatory Requirements", },
                    { id: 11210, title: "75 Percent FFP - General Regulatory Requirements", },
                    { id: 11215, title: "Access for State and Federal Inspection", },
                    { id: 11220, title: "Prospective Approval of Enhanced Funding", },
                    { id: 11225, title: "Considerations and Options", },
                    { id: 11227, title: "Acquisition of Adp Equipment and Services", },
                    { id: 11230, title: "Approval Process and Documentation Submissions", },
                    { id: 11235, title: "90 Percent FFP", },
                    { id: 11236, title: "Implementation Advance Planning Document (APD)", },
                    { id: 11237, title: "Detailed Implementation Schedule (DIS)", },
                    { id: 11238, title: "Project Reporting Requirements", },
                    { id: 11240, title: "75 Percent FFP - Federal Certification Review Process", },
                    { id: 11241, title: "Preliminary Evaluation", },
                    { id: 11242, title: "Onsite Observation", },
                    { id: 11243, title: "Post-Site Evaluation", },
                    { id: 11250, title: "Reimbursable Costs for State MMIS", },
                    { id: 11255, title: "Transition Funding--90- and 75-Percent FFP", },
                    { id: 11260, title: "Retroactive 75 Percent FFP", },
                ]
            },
            {
                id: "11265 to 11276.5",
                title: "Chapter 2 - Approval of MMIS Systems",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041213235006/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11265_to_11276.5.asp",
                    date: 1998
                },
                pdf: { date: 1998 },
                subsections: [
                    { id: 11265, title: "Contractual Services", },
                    { id: 11266, title: "Request for Proposal (RFP)", },
                    { id: 11268, title: "Cost Allocation Plan", },
                    { id: 11269, title: "Replacement Systems", },
                    { id: 11270, title: "Reserved", },
                    { id: 11276, title: "Costs Related to MMIS Design, Development, Installation, Operation, and Enhancement", },
                ]
            },
            {
                id: "11276 to 11282.1",
                title: "Chapter 2 - Approval of MMIS Systems",
                zip: { date: 1998 },
                web: { date: "unavailable" },
                pdf: { date: 1998 },
            },
            {
                id: "11300 to 11350",
                title: "Chapter 3 - System Requirements",
                zip: { date: 1998 },
                web: {
                    url: "https://web.archive.org/web/20041213120930/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11300_to_11350.asp",
                    date: 1998
                },
                pdf: { date: 1998 },
                subsections: [
                    { id: 11300, title: "General Requirements", },
                    { id: 11301, title: "Future Additional System Requirements", },
                    { id: 11310, title: "MMIS Functional Requirements", },
                    { id: 11315, title: "Recipient Subsystem", },
                    { id: 11320, title: "Provider Subsystem", },
                    { id: 11325, title: "Claims Processing Subsystem", },
                    { id: 11330, title: "Reference File Subsystem", },
                    { id: 11335, title: "Surveillance and Utilization Review (SUR) Subsystem", },
                    { id: 11340, title: "Management and Administrative Reporting (MAR) Subsystem", },
                    { id: 11350, title: "MARS and SURS Reports", },
                ]
            },
            {
                id: 11375,
                title: "Chapter 3 - System Requirements - Data Requirements",
                zip: { date: 2015 },
                web: {
                    url: "https://web.archive.org/web/20041213005333/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11375.asp",
                    date: 1998
                },
                pdf: { date: 1998 },
            },
            {
                id: "11600 to 11606",
                title: "Chapter 6 - CPAS Review Process",
                zip: { date: 1985 },
                web: {
                    url: "https://web.archive.org/web/20041213120934/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11600_to_11606.asp",
                    date: 1985
                },
                pdf: { date: 1985 },
                subsections: [
                    { id: 11600, title: "Background", },
                    { id: 11601, title: "Overview of CPAS", },
                    { id: 11604, title: "Mandatory System", },
                    { id: 11606, title: "Alternate System", },
                ]
            },
            {
                id: "11607 to 11609",
                title: "Chapter 6 - CPAS Review Process",
                zip: { date: 1985 },
                web: {
                    url: "https://web.archive.org/web/20041213233451/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11607_to_11609.asp",
                    date: 1985
                },
                pdf: { date: 1985 },
                subsections: [
                    { id: 11607, title: "CPAS Plan", },
                    { id: 11608, title: "General Requirements for Mandatory System Sample Selection", },
                    { id: 11609, title: "Documentation Source Sheet", },
                ]
            },
            {
                id: "11610 to 11611",
                title: "Chapter 6 - CPAS Review Process",
                zip: { date: 1985 },
                web: {
                    url: "https://web.archive.org/web/20041213234016/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11610_to_11611.asp",
                    date: 1985
                },
                pdf: { date: 1985 },
                subsections: [
                    { id: 11610, title: "Contents of the State CPAS File", },
                    { id: 11611, title: "CPAS Corrective Action", },
                ]
            },
            {
                id: "",
                zip: { date: "no date" },
                title: "Legal Background And Authority",
                web: { date: "unavailable" },
                pdf: { date: "no date" },
            },
        ],
    },
    {
        id: 13,
        title: "Part 13 – State Plan Procedures and Preprints",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_13.zip",
            date: "1984"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222106/http://www.cms.hhs.gov/manuals/pub45pdf/smm13t.pdf",
            date: "1984"
        },
        web: {
            url: "https://web.archive.org/web/20041212234952/http://www.cms.hhs.gov/manuals/45_smm/sm_13_13_toc.asp",
            date: "1984"
        },
        subsections: [
            {
                id: 13025,
                title: "State Plans and Plan Amendments - General",
                zip: { date: 1984 },
                web: {
                    url: "https://web.archive.org/web/20041213113241/http://www.cms.hhs.gov/manuals/45_smm/sm_13_13025_to_13100.asp#_toc490633729",
                    date: 1984
                },
                pdf: { date: 1984 },
            },
            {
                id: 13026,
                title: "Approval of State Plans and Amendments",
                zip: { date: 1984 },
                web: {
                    url: "https://web.archive.org/web/20041213113241/http://www.cms.hhs.gov/manuals/45_smm/sm_13_13025_to_13100.asp#_toc490633730",
                    date: 1984
                },
                pdf: { date: 1984 },
            },
            {
                id: 13100,
                title: "Inclusion of Waiver Provisions in the Approved State Medicaid Plan",
                zip: { date: 1984 },
                web: {
                    url: "https://web.archive.org/web/20041213113241/http://www.cms.hhs.gov/manuals/45_smm/sm_13_13025_to_13100.asp#_toc490633731",
                    date: 1984
                },
                pdf: { date: 1984 },
            },
        ],
    },
    {
        id: 15,
        title: "Part 15 - Income and Eligibility Verification System",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_15.zip",
            date: "1991"
        },
        web: {
            url: "https://web.archive.org/web/20041212235650/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15_toc.asp",
            date: "1991"
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222351/http://www.cms.hhs.gov/manuals/pub45pdf/smm15t.pdf",
            date: "1991"
        },
        subsections: [
            {
                id: 15800,
                title: "Background of Income and Eligibility Verification System (IEVS)",
                zip: { date: 1989 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634424",
                    date: 1989
                },
                pdf: { date: 1989 },
            },
            {
                id: 15801,
                title: "Requests for Information and Data Exchanges",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634425",
                    date: 1991
                },
                pdf: { date: 1991 },
            },
            {
                id: 15802,
                title: "Use and Verification of Social Security Number (SSN)",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634426",
                    date: 1991
                },
                pdf: { date: 1991 },
            },
            {
                id: 15803,
                title: "Use and Verification of Information",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634427",
                    date: 1991
                },
                pdf: { date: 1991 },
            },
            {
                id: 15804,
                title: "Targeting the Use of Income and Eligibility Verification System (IEVS) Data",
                zip: { date: 1991 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634428",
                    date: 1991
                },
                pdf: { date: 1991 },
            },
            {
                id: 15805,
                title: "Alternate Sources of Data",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634429",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 15806,
                title: "State Plan Requirement",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634430",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
            {
                id: 15807,
                title: "Safeguard Requirements for IRS Unearned Income Data",
                zip: { date: 1989 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634431",
                    date: 1989
                },
                pdf: { date: 1989 },
            },
            {
                id: "Exhibit 1",
                title: "Safeguard Activity Report",
                zip: { date: "no date" },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634432",
                    date: "no date"
                },
                pdf: { date: "no date" },
            },
            {
                id: 15808,
                title: "Recordkeeping and Data Management",
                zip: { date: 1990 },
                web: {
                    url: "https://web.archive.org/web/20041213114018/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15800_to_15808.asp#_toc490634433",
                    date: 1990
                },
                pdf: { date: 1990 },
            },
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
                <div class="">
                    <p class="manual-page-description">
                        This page provides links to
                        <a
                            class="external"
                            target="_blank"
                            href="https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927"
                        >
                            zipped Word documents from the CMS website
                        </a>
                        , which is the most current and complete version of the manual,
                        along with links to convenient
                        <a
                            class="external"
                            target="_blank"
                            href="https://web.archive.org/web/20041212094406/http://www.cms.hhs.gov/manuals/45_smm/pub45toc.asp"
                        >
                            web pages
                        </a>
                        and
                        <a
                            class="external"
                            target="_blank"
                            href="https://web.archive.org/web/20050204151206/http://www.cms.hhs.gov:80/manuals/pub45pdf/smmtoc.asp"
                        >
                            PDFs
                        </a>
                        from archived copies of the CMS website.
                    </p>
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
                                <template v-for="section in sections" :key="section.id">
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
                                                v-if="section.zip?.url"
                                                :href="section.zip.url"
                                                target="_blank"
                                                class="link-btn"
                                            >
                                                Word
                                                <span v-if="section.zip.date" class="date-stamp">
                                                    ({{ section.zip.date }})
                                                </span>
                                            </a>
                                        </td>
                                        <td class="table__cell">
                                            <a
                                                v-if="section.web?.url"
                                                :href="section.web.url"
                                                target="_blank"
                                                class="link-btn"
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
                                                    <span v-if="sub.zip?.date" class="date-stamp">
                                                        ({{ sub.zip.date }})
                                                    </span>
                                                </td>
                                                <td class="table__cell">
                                                    <a
                                                        v-if="sub.web?.url"
                                                        :href="sub.web.url"
                                                        target="_blank"
                                                        class="link-btn"
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
                                                        <span v-if="nestedSub.zip?.date" class="date-stamp">
                                                            ({{ nestedSub.zip.date }})
                                                        </span>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a
                                                            v-if="nestedSub.web?.url"
                                                            :href="nestedSub.web.url"
                                                            target="_blank"
                                                            class="link-btn"
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
    vertical-align: top;
    padding: 1rem;
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

.sticky {
    position: sticky;
    top: 0;
    z-index: 100;
}

.nested-subsection-cell {
    padding-left: 4rem;
    font-size: 0.95rem;
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
