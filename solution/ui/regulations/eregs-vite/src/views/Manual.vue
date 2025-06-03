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
                        url: "https://web.archive.org/web/20041211222603/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867857",
                        date: ""
                    } },
                    { id: 2081, title: "Subcontracts", web: {
                        url: "https://web.archive.org/web/20041211222603/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867876",
                        date: ""
                    } },
                    { id: 2082, title: "Specific Requirements for Fiscal Agent Contracts", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867879",
                        date: ""
                    } },
                    { id: 2083, title: "Procurement Procedures and Policies for State Medicaid Contracts", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867883",
                        date: ""
                    } },
                    { id: 2084, title: "Medicare and Medicaid Health and Safety Standards", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867890",
                        date: ""
                    } },
                    { id: 2085, title: "Specific Requirements for Health Maintenance Organizations (HMOs) and Certain Health Insuring Organizations (HIOs)", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867897",
                        date: ""
                    } },
                    { id: 2086, title: "Eligibility for FFP", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867901",
                        date: ""
                    } },
                    { id: 2087, title: "HMO and Certain HIO Contracts - General", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867918",
                        date: ""
                    } },
                    { id: 2088, title: "Enrollees and Benefits", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867929",
                        date: ""
                    } },
                    { id: 2089, title: "Capitation Payments", web: {
                        url: "https://web.archive.org/web/20041211162316/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2080_to_2089.9.asp#_Toc489867939",
                        date: ""
                    } },
                ]
            },
            { 
                id: "2090 to 2092.9",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211221428/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2090_to_2092.9.asp",
                    date: "1992"
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929140914/http://www.hcfa.gov:80/pubforms/pub45pdf/20902.pdf",
                    date: "1992"
                },
                subsections: [
                    { id: 2090, title: "Marketing, Enrollment and Disenrollment", date: "" },
                    { id: 2091, title: "Quality Assurance", date: "" },
                    { id: 2092, title: "Additional State Agency Responsibilities", date: "" },
                ]
            },
            { 
                id: "2100 to 2106.2",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211221711/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2100_to_2106.2.asp",
                    date: "1994"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910143952/http://cms.gov:80/manuals/pub45pdf/2100.pdf",
                    date: "1994"
                },
                subsections: [
                    { id: 2100, title: "Free Choice of Providers - General", date: "" },
                    { id: 2101, title: "Informing Beneficiaries", date: "" },
                    { id: 2102, title: "Contractual Arrangements", date: "" },
                    { id: 2103, title: "Exceptions to Freedom of Choice", date: "" },
                    { id: 2104, title: "Waiver of State Plan Requirements", date: "" },
                    { id: 2105, title: "Categories of Waivers Under §1915(b)", date: "" },
                    { id: 2106, title: "How to Submit Request for Waiver Under §1915(b)", date: "" },
                ]
            },
            { 
                id: "2106.3 to 2493",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211222317/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2106.3_to_2493.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20051208033356/http://www.cms.hhs.gov:80/manuals/pub45pdf/21063.pdf",
                    date: "1991"
                },
                subsections: [
                    { id: 2106, title: "How to Submit Request for Waiver Under §1915(b)", date: "" },
                    { id: 2107, title: "Documentation Required When Submitting Requests for Waiver Under Section 1915(b)", date: "" },
                    { id: 2108, title: "Documentation of Cost Effectiveness, Access to Care, Quality of Care and Projected Impact of Waiver on the Medicaid Program", date: "" },
                    { id: 2109, title: "Requests for Modification of an Approved Waiver Program", date: "" },
                    { id: 2110, title: "Waiver Renewals", date: "" },
                    { id: 2111, title: "Monitoring, Evaluation, and Termination of Waivers", date: "" },
                    { id: 2112, title: "Freedom of Choice - Family Planning Services Under §1915(b)", date: "" },
                    { id: 2113, title: "Transportation to Providers of Services", date: "" },
                    { id: 2114, title: "Case Management for Which No Waiver Is Required", date: "" },
                    { id: 2200, title: "Requirements for Advance Directives Under State Plans for Medical Assistance", date: "" },
                    { id: 2350, title: "Legislative Background", date: "" },
                    { id: 2351, title: "State-PSRO Contracting Process", date: "" },
                    { id: 2352, title: "Plan Amendment", date: "" },
                    { id: 2353, title: "Functions Under the State-PSRO Contract", date: "" },
                    { id: 2354, title: "State Agency Jurisdiction for Hearing and Appeals", date: "" },
                    { id: 2355, title: "Responsibilities of a State That Does Not Contract With a PSRO", date: "" },
                    { id: 2356, title: "Transition Issues", date: "" },
                    { id: 2450, title: "Conflict of Interest Provisions", date: "" },
                    { id: 2451, title: "Definitions", date: "" },
                    { id: 2452, title: "Prohibited Activities", date: "" },
                    { id: 2490, title: "Claiming Federal Financial Participation (FFP) for Advance Payments Made to Providers of Medical Assistance Under Title XIX of the Social Security Actfederal Financial Participation", date: "" },
                    { id: 2493, title: "Claiming FFP for Provider Payments for State Taxes", date: "" },
                ]
            },
            { 
                id: "2495 to 2500.1",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211220824/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2495_to_2500.1.asp",
                    date: "1991"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910235317/http://cms.gov:80/manuals/pub45pdf/2495.pdf",
                    date: "1991"
                },
                subsections: [
                    { id: 2495, title: "Maintenance of Effort", date: "" },
                    { id: 2497, title: "Documentation Required to Support a Claim for Federal Financial Participation", date: "" },
                    { id: 2500, title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program", date: "" },
                ]
            },
            { id: "2500.2 to 2500.6", title: "Quarterly Medicaid Statement of Expenditures for the Medical Assistance Program", date: "" },
            { 
                id: "2501 to 2555",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211221703/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2501_to_2555.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911060906/http://cms.gov:80/manuals/pub45pdf/2501.pdf",
                    date: ""
                },
                subsections: [
                    { id: 2501, title: "Federal Medical Assistance Percentages (FMAP) - State-by-State Tables", date: "" },
                    { id: 2502, title: "Interest on Disputed Medicaid Claims", date: "" },
                    { id: 2504, title: "Deeming and Waiver of Nurse Aide Training and Competency Evaluation Requirements", date: "" },
                    { id: 2505, title: "Nurse Aide Training and Competency Evaluation Programs and Competency Evaluation Programs", date: "" },
                    { id: 2514, title: "Federal Financial Participation (FFP) for Nurse Aide Training and Competency Evaluation Programs (NATCEPs) and Competency Evaluation Programs (CEPs).", date: "" },
                    { id: 2515, title: "Federal Financial Participation for Preadmission Screening and Annual Resident Review (PASARR) Activities", date: "" },
                    { id: 2555, title: "Information on Target Expenditure Levels, Reductions in Medicaid Payments, and Computation of Incentive Rebates to States", date: "" },
                ]
            },
            { 
                id: "2560 to 2600.2",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211222048/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2560_to_2600.2.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911084821/http://cms.gov:80/manuals/pub45pdf/2560.pdf",
                    date: ""
                },
                subsections: [
                    { id: 2560, title: "Medicaid Funding Limitations Policy", date: "" },
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program", date: "" },
                ]
            },
            { id: "2600.3 to 2600.10", title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program", web: {
                url: "https://web.archive.org/web/20041211221749/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2600_to_2600.10.asp",
                date: ""
            }, pdf: {
                url: "https://web.archive.org/web/20000929140950/http://www.hcfa.gov:80/pubforms/pub45pdf/26003.pdf",
                date: ""
            } },
            { 
                id: "2600.11 to 2602",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211221327/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2600.11_to_2602.asp",
                    date: ""
                },
                subsections: [
                    { id: 2600, title: "Quarterly Budget Estimates - Grants to States for Medical Assistance Program", date: "" },
                    { id: 2602, title: "Submission Schedule - Medicaid Program Budget Report (Form HCFA-25)", date: "" },
                ]
            },
            { id: "2700 to 2700.2", title: "Federal Reporting Requirements", web: {
                url: "https://web.archive.org/web/20041211221832/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700_to_2700.2.asp",
                date: ""
            }, pdf: {
                url: "https://web.archive.org/web/20030910161000/http://cms.gov:80/manuals/pub45pdf/2700.pdf",
                date: ""
            } },
            { id: "2700.4", title: "Federal Reporting Requirements", web: {
                url: "https://web.archive.org/web/20041211222643/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700.4_to_2700.4.asp",
                date: ""
            }, pdf: {
                url: "https://web.archive.org/web/20030910202813/http://cms.gov:80/manuals/pub45pdf/27004.pdf",
                date: ""
            } },
            { id: "2700.6", title: "Federal Reporting Requirements", web: {
                url: "https://web.archive.org/web/20041211050529/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2700.6_to_2700.6.asp",
                date: ""
            }, pdf: {
                url: "https://web.archive.org/web/20000929141011/http://www.hcfa.gov:80/pubforms/pub45pdf/27006.pdf",
                date: ""
            } },
            { 
                id: "2850 to 2853.5",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211164736/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2850_to_2853.5.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141015/http://www.hcfa.gov:80/pubforms/pub45pdf/2850.pdf",
                    date: ""
                },
                subsections: [
                    { id: 2850, title: "Withholding the Federal Share of Payments to Medicaid Providers to Recover Medicare Overpayments; Withholding Medicare Payments to Recover Medicaid Overpayments", date: "" },
                    { id: 2851, title: "Procedures Required of the Medicaid State Agency to Implement Section 1914", date: "" },
                    { id: 2852, title: "Procedures Required of the Medicaid State Agency to Implement Section 1885", date: "" },
                    { id: 2853, title: "Procedures for Refunding the Federal Share of Medicaid Overpayments", date: "" },
                ]
            },
            { 
                id: "2900.2 to 2975.6",
                title: "",
                web: {
                    url: "https://web.archive.org/web/20041211222256/http://www.cms.hhs.gov/manuals/45_smm/sm_02_2_2900.2_to_2975.6.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141021/http://www.hcfa.gov:80/pubforms/pub45pdf/2900.pdf",
                    date: ""
                },
                subsections: [
                    { id: 2900, title: "Fair Hearings and Appeals", date: "" },
                    { id: 2901, title: "Notice and Opportunity for a Fair Hearing", date: "" },
                    { id: 2902, title: "Hearings", date: "" },
                    { id: 2903, title: "Hearing Decision", date: "" },
                    { id: 2904, title: "Reopening and Recovery", date: "" },
                    { id: 2905, title: "Outstationing of Eligibility Workers General", date: "" },
                    { id: 2906, title: "Outstation Locations", date: "" },
                    { id: 2907, title: "Staffing at Outstation Locations", date: "" },
                    { id: 2908, title: "Guidelines for Outstationing and Providing Application Assistance at Low Use Locations", date: "" },
                    { id: 2909, title: "Limitations on Outstationed Eligibility Workers", date: "" },
                    { id: 2910, title: "Application Process", date: "" },
                    { id: 2911, title: "Applications", date: "" },
                    { id: 2912, title: "Compliance With Federal Regulations", date: "" },
                    { id: 2913, title: "FFP for Outstationing", date: "" },
                    { id: 2975, title: "Contingency Fee Reimbursement for Third Party Liability Identification or Collection", date: "" },
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
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20000929141030/http://www.hcfa.gov:80/pubforms/pub45pdf/sm3200.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3200, title: "Changes Due to Welfare Reform", date: "" },
                    { id: 3207, title: "Changes in SSI Definition of Disability Due to Welfare Reform", date: "" },
                ]
            },
            { 
                id: "3210 to 3256",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20041213002635/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3210_to_3256.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030808034231/http://www.cms.hhs.gov/manuals/pub45pdf/sm3210.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3210, title: "Citizenship and Alienage", date: "" },
                    { id: 3211, title: "Aliens", date: "" },
                    { id: 3212, title: "Documentation and Verification of Status as Citizen or Alien", date: "" },
                    { id: 3213, title: "Redeterminations and FFP Availability", date: "" },
                    { id: 3215, title: "Treatment of Potential Payments From Medicaid Qualifying Trust", date: "" },
                    { id: 3230, title: "State Residence", date: "" },
                    { id: 3240, title: "More Liberal Income and Resource Methods", date: "" },
                    { id: 3250, title: "Transfer of Resources", date: "" },
                    { id: 3255, title: "Elimination of SSI Provision on Resources Transferred for Less Than Fair Market Value and Notification by SSA", date: "" },
                    { id: 3256, title: "Transfer of Resources Procedures", date: "" },
                ]
            },
            { 
                id: "3257 to 3259.8",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20041213121554/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3257_to_3259.8.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20040625034414/http://cms.hhs.gov:80/manuals/pub45pdf/sm3257.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3257, title: "Transfers of Assets and Treatment of Trusts Transfers of Assets for Less Than Fair Market Value", date: "" },
                    { id: 3258, title: "Transfers of Assets for Less Than Fair Market Value", date: "" },
                    { id: 3259, title: "Treatment of Trusts", date: "" },
                ]
            },
            { 
                id: "3260 to 3280.2",
                title: "Chapter III - General And Categorical Eligibility Requirements",
                web: {
                    url: "https://web.archive.org/web/20040808075206/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3260.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910145847/http://cms.gov:80/manuals/pub45pdf/sm3260.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3260, title: "Income and Resource Eligibility Rules for Certain Institutionalized Individuals and Certain Individuals Under Home and Community-Based Waivers Who Have Community Spouses", date: "" },
                    { id: 3261, title: "Income Eligibility", date: "" },
                    { id: 3262, title: "Resource Assessments and Eligibility", date: "" },
                    { id: 3263, title: "Notice, Hearings and Appeals", date: "" },
                    { id: 3270, title: "Disability Determinations Under Medicaid", date: "" },
                    { id: 3271, title: "Disability Determinations in §1902(f) States and SSI Criteria States", date: "" },
                    { id: 3272, title: "Medicaid Eligibility Quality Control (MEQC) Treatment of Payments Made During Period You Made a Reasonable Application of SSI Disability Criteria", date: "" },
                    { id: 3273, title: "Composition of Disability Review Teams", date: "" },
                    { id: 3274, title: "Procedures for Making Disability Determinations", date: "" },
                    { id: 3275, title: "Coordination Between State Medicaid Agency and the SSA Disability Determination Service (DDS)", date: "" },
                    { id: 3276, title: "Referral to SSA", date: "" },
                    { id: 3277, title: "Time Limit to Determine Eligibility in Disability Cases", date: "" },
                    { id: 3280, title: "Mandatory Coordination With WIC", date: "" },
                ]
            },
            { 
                id: "3300 to 3314.2",
                title: "Chapter IV - Mandatory Coverage of Categorically Needy Families and Children",
                web: {
                    url: "https://web.archive.org/web/20040808081605/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3300_to_3314.2.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910181119/http://cms.gov:80/manuals/pub45pdf/sm3300.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3300, title: "Introduction", date: "" },
                    { id: 3301, title: "Low Income Families With Children", date: "" },
                    { id: 3302, title: "Individuals Deemed to Be Recipients of AFDC", date: "" },
                    { id: 3303, title: "Qualified Pregnant Women", date: "" },
                    { id: 3304, title: "Qualified Children", date: "" },
                    { id: 3305, title: "Deemed Eligibility of Newborns", date: "" },
                    { id: 3306, title: "Extended Medicaid Coverage for Pregnant Women", date: "" },
                    { id: 3307, title: "Continuous Eligibility", date: "" },
                    { id: 3308, title: "Extended Medicaid Benefits to Families Who Lose AFDC Because of Earnings From Employment or Loss of Earnings Disregards", date: "" },
                    { id: 3309, title: "Qualified Family Members", date: "" },
                    { id: 3311, title: "Mandatory Coverage for Low Income Pregnant Women and Infants", date: "" },
                    { id: 3312, title: "Mandatory Coverage for Low Income Children Under Age 6", date: "" },
                    { id: 3313, title: " Mandatory Coverage for Low Income Children Under Age 19", date: "" },
                    { id: 3314, title: "Extended Medicaid Benefits to Families Who Lose Eligibility Because of Income From Support Payments", date: "" },
                ]
            },
            { 
                id: 3405, 
                title: "Changes Due to Welfare Reform", 
                web: {
                    url: "https://web.archive.org/web/20040808082505/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3405_to_3405.asp",
                    date: "1997"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030910213015/http://cms.gov/manuals/pub45pdf/sm3405.pdf",
                    date: "1997"
                },
            },
            { 
                id: "3410 to 3493",
                title: "Chapter V - Mandatory Coverage of the Aged, Blind, and Disabled",
                web: {
                    url: "https://web.archive.org/web/20040808082726/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3410_to_3493.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20031127050455/http://www.cms.gov:80/manuals/pub45pdf/sm3410.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3410, title: "Medicaid Eligibility for Qualified Severely Impaired Individuals and Individuals in §1619 Status", date: "" },
                    { id: 3411, title: "Provisions of OBRA1986 and EODAA", date: "" },
                    { id: 3412, title: "Operational Considerations", date: "" },
                    { id: 3420, title: "Individuals in States Using More Restrictive Eligibility Requirements", date: "" },
                    { id: 3435, title: "Persons With Drug Addiction or Alcoholism", date: "" },
                    { id: 3485, title: "Coverage of Qualified Disabled and Working Individuals", date: "" },
                    { id: 3490, title: "Coverage of Qualified Medicare Beneficiaries for Medicare Cost Sharing Expenses", date: "" },
                    { id: 3491, title: "Coverage of Specified Low Income Medicare Beneficiaries for Medicare Part B Premiums", date: "" },
                    { id: 3492, title: "Coverage of Qualifying Individuals for Medicare Part B Premiums", date: "" },
                    { id: 3493, title: "Medicaid Eligibility for Disabled Children Who Lose SSI Payment", date: "" },
                ]
            },
            { 
                id: "3500 to 3599.4",
                title: "Chapter VI - Optional Coverage of Categorically Needy Groups",
                web: {
                    url: "https://web.archive.org/web/20040808084030/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3500_to_3599.4.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030805123125/http://www.cms.hhs.gov:80/manuals/pub45pdf/sm3500.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3500, title: "Introduction", date: "" },
                    { id: 3501, title: "Definitions", date: "" },
                    { id: 3502, title: "Persons Who Meet Income and Resource Requirements for, but Do Not Receive Cash Assistance", date: "" },
                    { id: 3503, title: "Children Under Age 21", date: "" },
                    { id: 3504, title: "Reserved", date: "" },
                    { id: 3505, title: "Reserved", date: "" },
                    { id: 3506, title: "Children Under State Adoption Assistance Programs", date: "" },
                    { id: 3570, title: "Optional Presumptive Eligibility Period for Pregnant Women", date: "" },
                    { id: 3571, title: "Optional Coverage for Poor Pregnant (And Postpartum) Women, Infants and Children", date: "" },
                    { id: 3580, title: "Hospice Benefits", date: "" },
                    { id: 3581, title: "Optional Hospice Care Eligibility Group", date: "" },
                    { id: 3582, title: "Comparability of Hospice Care Benefits", date: "" },
                    { id: 3583, title: "Copayments on Hospice Care Benefits", date: "" },
                    { id: 3584, title: "Post-Eligibility Treatment of Income for Hospice Care", date: "" },
                    { id: 3589, title: "Medicaid Coverage of Home Care for Certain Disabled Children", date: "" },
                    { id: 3590, title: "Individuals Eligible for Services Under a Home and Community-Based Services Waiver", date: "" },
                    { id: 3596, title: "Optional Coverage of the Elderly and Disabled Poor for All Medicaid Benefits", date: "" },
                    { id: 3597, title: "Treatment of Couples in Medical Institutions", date: "" },
                    { id: 3598, title: "Coverage of COBRA Continuation Beneficiaries", date: "" },
                    { id: 3599, title: "Buy-In to Medicaid for the Working Disabled", date: "" },
                ]
            },
            { 
                id: "3600 to 3645.6",
                title: "Chapter VII - Coverage of the Medically Needy",
                web: {
                    url: "https://web.archive.org/web/20040808070458/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3600_to_3645.6.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911083221/http://cms.gov:80/manuals/pub45pdf/sm3600.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3600, title: "Introduction", date: "" },
                    { id: 3601, title: "Background", date: "" },
                    { id: 3610, title: "Eligible Groups", date: "" },
                    { id: 3611, title: "Required Groups", date: "" },
                    { id: 3612, title: "Optional Eligible Groups", date: "" },
                    { id: 3613, title: "Criteria for Determining Categorically Needy and Medically Needy", date: "" },
                    { id: 3620, title: "Financial Eligibility", date: "" },
                    { id: 3621, title: "Single Income and Resource Standard", date: "" },
                    { id: 3622, title: "Cost of Living Variations", date: "" },
                    { id: 3623, title: "Defining Reasonable Standards", date: "" },
                    { id: 3624, title: "Federal Financial Participation (FFP) Limitation", date: "" },
                    { id: 3625, title: "Financial Methodologies", date: "" },
                    { id: 3626, title: "Income Eligibility", date: "" },
                    { id: 3627, title: "Budget Periods", date: "" },
                    { id: 3628, title: "Deduction of Incurred Medical and Remedial Care Expenses (Spenddown)", date: "" },
                    { id: 3630, title: "Resource Eligibility", date: "" },
                    { id: 3640, title: "Moratorium", date: "" },
                    { id: 3645, title: "Pay-In Spenddown Option", date: "" },
                ]
            },
            { 
                id: "3700 to 3714.2",
                title: "Chapter VIII - Post-Eligibility",
                web: {
                    url: "https://web.archive.org/web/20040808074001/http://www.cms.hhs.gov/manuals/45_smm/sm_03_3_3700_to_3714.2.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20050524160719/http://www.cms.hhs.gov:80/manuals/pub45pdf/sm3700.pdf",
                    date: ""
                },
                subsections: [
                    { id: 3700, title: "Introduction", date: "" },
                    { id: 3701, title: "General Statement of Post-Eligibility Process", date: "" },
                    { id: 3702, title: "Deductions From the Individual's Total Income", date: "" },
                    { id: 3703, title: "Required Deductions", date: "" },
                    { id: 3704, title: "Optional Deductions", date: "" },
                    { id: 3705, title: "Post-Eligibility Treatment of Certain Payments Made by the Department of Veterans Affairs", date: "" },
                    { id: 3708, title: "Post-Eligibility Treatment of Certain Disabled Institutionalized Individuals", date: "" },
                    { id: 3710, title: "Special Post-Eligibility Process for Institutionalized Persons With Community Spouses", date: "" },
                    { id: 3711, title: "Income Used in the Post-Eligibility Process", date: "" },
                    { id: 3712, title: "Mandatory Deductions From Income", date: "" },
                    { id: 3713, title: "Monthly Income Allowances for Community Spouses and Other Family Members", date: "" },
                    { id: 3714, title: "Notice, Hearings and Appeals", date: "" },
                ]
            },
            { 
                id: "3800 to 3812",
                title: "Chapter IX - Financial Eligibility Requirements and Options",
                zip: {
                    date: "1994"
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
                    { id: 3810, title: "Medicaid Estate Recoveries", date: "" },
                    { id: 3812, title: "Treatment of Contributions From Relatives to Medicaid Applicants or Recipients", date: "" },
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
                    { id: 3900, title: "Third Party Liability (TPL)", date: "" },
                    { id: 3901, title: "Definitions", date: "" },
                    { id: 3902, title: "General TPL Requirements", date: "" },
                    { id: 3903, title: "Identification of Resources (42 CFR 433.138)", date: "" },
                    { id: 3904, title: "Payment of Claims (42 CFR 433.139)", date: "" },
                    { id: 3905, title: "Assignment of Rights to Benefits - (42 CFR 433.145)", date: "" },
                    { id: 3906, title: "Cooperative Agreements and Incentive Payments", date: "" },
                    { id: 3907, title: "Distribution of Collections", date: "" },
                    { id: 3908, title: "Conflicting Claims by Medicare and Medicaid", date: "" },
                    { id: 3909, title: "Medicare/Medicaid Crossover Claims", date: "" },
                    { id: 3910, title: "Medicaid Payments for Recipients Under Group Health Plans", date: "" },
                ]
            },
            { 
                id: "IM 3570", 
                title: "Requirements for Eligibility Under a Special Income Level", 
                zip: {
                    date: ""
                },
                web: {
                    url: "https://web.archive.org/web/20040227225635/http://www.cms.hhs.gov/manuals/45_smm/sm_03_im_3570.asp",
                    date: "1986"
                },
            },
            { 
                id: "IM 3900", 
                title: "Third Party Liability (TPL)", 
                zip: {
                    date: ""
                },
                web: {
                    url: "https://web.archive.org/web/20040808080724/http://www.cms.hhs.gov/manuals/45_smm/sm_03_im_3900_to_im_3900.asp",
                    date: "1994"
                },
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
                web: {
                    url: "https://web.archive.org/web/20041206171539/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4130_to_4253.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20050110002858/http://cms.hhs.gov:80/manuals/pub45pdf/sm4130.pdf",
                    date: ""
                },
                subsections: [
                    { id: 4130, title: "Comparability of Services", date: "" },
                    { id: 4201, title: "Organ Transplants", date: "" },
                    { id: 4221, title: "Outpatient Psychiatric Services.", date: "" },
                    { id: 4231, title: "Federally Qualified Health Center (FQHC) and Other Ambulatory Services", date: "" },
                    { id: 4250, title: "Minimum Federal Criteria for States to Use in Making Preadmission and Annual Review Determinations About Admission to or Continued Residence in Nursing Facilities for Individuals Who Have Mental Illness or Mental Retardation", date: "" },
                    { id: 4251, title: "Minimum Evaluation Criteria Specific to Screening Persons With MR or MI for the Need for NF Level of Services (PASARR/NF)", date: "" },
                    { id: 4252, title: "Minimum Criteria Specific to the Screening of Persons With MI (PASARR/MI)", date: "" },
                    { id: 4253, title: "Minimum Criteria Specific to the Screening for Persons With MR (PASARR/MR)", date: "" },
                ]
            },
            { 
                id: "4270 to 4390.1",
                title: "Requirements and Limits Applicable to Specific Services",
                web: {
                    url: "https://web.archive.org/web/20041206172221/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4270_to_4390.1.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20040503210948/http://cms.hhs.gov:80/manuals/pub45pdf/sm4270.pdf",
                    date: ""
                },
                subsections: [
                    { id: 4270, title: "Family Planning Services", date: "" },
                    { id: 4280, title: "Establishment and Use of Medicaid Unique Physician Identifier", date: "" },
                    { id: 4281, title: "Restriction on Payments for Physician Services", date: "" },
                    { id: 4282, title: "Maintenance of List of Physicians by States", date: "" },
                    { id: 4283, title: "Conditions for Foreign Medical Graduate Certification", date: "" },
                    { id: 4301, title: "Home Respiratory Care for Ventilator-Dependent Individuals", date: "" },
                    { id: 4302, title: "Optional Targeted Case Management Services - Basis, Scope and Purpose", date: "" },
                    { id: 4305, title: "Hospice Services", date: "" },
                    { id: 4306, title: "Hospice Reimbursement", date: "" },
                    { id: 4307, title: "Payment for Physician Services Under Hospice", date: "" },
                    { id: 4308, title: "Optional Cap on Overall Hospice Reimbursement", date: "" },
                    { id: 4310, title: "Private Duty Nursing Services", date: "" },
                    { id: 4320, title: "Clinic Services.", date: "" },
                    { id: 4370, title: "Less Than Effective and Identical, Related or Similar Drugs", date: "" },
                    { id: 4375, title: "Tuberculosis Related Services", date: "" },
                    { id: 4385, title: "Preventive Services", date: "" },
                    { id: 4390, title: "Institutions for Mental Diseases", date: "" },
                ]
            },
            { 
                id: "4395 to 4435.4",
                title: "Requirements and Limits Applicable to Specific Services",
                web: {
                    url: "https://web.archive.org/web/20041206172723/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4395_to_4435.4.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911004440/http://cms.gov:80/manuals/pub45pdf/sm4395.pdf",
                    date: ""
                },
                subsections: [
                    { id: 4395, title: "Inappropriate Placement of Mentally Retarded Persons in SNFs and ICFs", date: "" },
                    { id: 4396, title: "Application of the Educational Services Exclusion in ICFs/MR", date: "" },
                    { id: 4397, title: "Application of the Vocational Services Exclusion in ICFs/MR", date: "" },
                    { id: 4398, title: "Persons With Related Conditions", date: "" },
                    { id: 4415, title: "Nurse Practitioner Services", date: "" },
                    { id: 4420, title: "Nurse-Midwife Services", date: "" },
                    { id: 4421, title: "Services for Pregnant Women", date: "" },
                    { id: 4430, title: "Legal Background and Authority", date: "" },
                    { id: 4431, title: "Federal Funding of Abortions", date: "" },
                    { id: 4432, title: "Federal Funding of Abortion Related Services", date: "" },
                    { id: 4434, title: "Legal Background and Authority", date: "" },
                    { id: 4435, title: "Sterilization by Hysterectomy", date: "" },
                ]
            },
            { 
                id: "4440 to 4444",
                title: "Requirements and Limits Applicable to Specific Services",
                web: {
                    url: "https://web.archive.org/web/20041206161214/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4440_to_4444.asp",
                    date: ""
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911050125/http://cms.gov:80/manuals/pub45pdf/sm4440.pdf",
                    date: ""
                },
                subsections: [
                    { id: 4440, title: "Home and Community-Based Services - Basis, Scope, and Purpose", date: "" },
                    { id: 4441, title: "Home and Community-Based Services - Process", date: "" },
                    { id: 4442, title: "Waiver Request Requirements", date: "" },
                    { id: 4443, title: "Home and Community-Based Services - Model Waiver Request", date: "" },
                    { id: 4444, title: "Home and Community-Based Services - Procedures to Request", date: "" },
                ]
            },
            { 
                id: "4444 to 4658",
                title: "Requirements and Limits Applicable to Specific Services",
                web: {
                    url: "https://web.archive.org/web/20041206161854/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_4444_to_4658.asp",
                    date: "1999"
                },
                pdf: {
                    url: "https://web.archive.org/web/20030911080158/http://cms.gov:80/manuals/pub45pdf/sm4444.pdf",
                    date: "1999"
                },
                subsections: [
                    { id: "4444 (Continued)", title: "Home and Community-Based Services - Procedures to Request", date: "" },    
                    { id: 4445, title: "Home and Community-Based Services Amendments", date: "" },
                    { id: 4446, title: "Home and Community-Based Services Terminations", date: "" },
                    { id: 4460, title: "Nurse Aide Registry", date: "" },
                    { id: 4470, title: "Specification of Resident Assessment Instruments for Use in Long Term Care Facilities", date: "" },
                    { id: 4480, title: "Personal Care Services", date: "" },
                    { id: 4560, title: "Skilled Nursing Facility (SSF) and Intermediate Care Facility (ICF) Services Provided by Swing Bed Hospitals", date: "" },
                    { id: 4570, title: "Ambulatory Surgical Center Services.", date: "" },
                    { id: 4580, title: "Phlebotomy and Case Management Services Associated With the Drug Clozaril", date: "" },
                    { id: 4600, title: "Usage of Certification Transmittal, HCFA-1539", date: "" },
                    { id: 4601, title: "Usage of the Statement of Deficiencies and Plan of Correction, HCFA-2567", date: "" },
                    { id: 4602, title: "Provider Agreements", date: "" },
                    { id: 4603, title: "Readmission to the Medicare or Medicaid Program After Termination", date: "" },
                    { id: 4604, title: "Authority to Grant Life Safety Code Waivers for Medicaid Only NFs", date: "" },
                    { id: 4650, title: "Termination - General", date: "" },
                    { id: 4651, title: "Basis for Terminating Program Participation", date: "" },
                    { id: 4652, title: "Termination Procedures--Immediate and Serious Threat to Patient Health and Safety", date: "" },
                    { id: 4653, title: "Termination Procedures--Noncompliance Limits Capacity of Facility to Furnish Adequate Level or Quality of Care - No Immediate and Serious Threat to Health and Safety", date: "" },
                    { id: 4654, title: "Nonrenewal or Cancellation of Time Limited Agreements for Long Term Care Facilities (Medicare and Medicaid)", date: "" },
                    { id: 4655, title: "Notice of Termination", date: "" },
                    { id: 4656, title: "Additional Communications With Facility", date: "" },
                    { id: 4657, title: "Relocating Patients or Residents Displaced by Termination or Closure", date: "" },
                    { id: 4658, title: "Guidance to States for Medicaid Nursing Facility (NF) Remedies", date: "" },
                ]
            },
            { 
                id: "", 
                title: "Addendum A - Wage Indices for Urban Areas", 
                web: {
                    url: "https://web.archive.org/web/20041206162508/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_add_a.asp",
                    date: "1987"
                },
            },
            { 
                id: "", 
                title: "Addendum B - Wage Indices for Rural Areas", 
                web: {
                    url: "https://web.archive.org/web/20041206163143/http://www.cms.hhs.gov/manuals/45_smm/sm_04_4_add_b.asp",
                    date: "1987"
                },
            },
            { 
                id: "IM 4604", 
                title: "Change in Authority to Grant Life Safety Code Waivers for Medicaid Only NFs", 
                web: {
                    url: "https://web.archive.org/web/20041206164106/http://www.cms.hhs.gov/manuals/45_smm/sm_04_im_4604.asp",
                    date: "1991"
                },
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
        ],
    },
    {
        id: 6,
        title: "Part 6 – Payments for Services",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_06.zip",
            date: ""
        },
        pdf: {
            url: "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/smm6t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041212235830/http://www.cms.hhs.gov/manuals/45_smm/sm_06_6_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 7,
        title: "Part 7 – Quality Control",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_07.zip",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222046/http://www.cms.hhs.gov/manuals/pub45pdf/smm7t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041205032506/http://www.cms.hhs.gov/manuals/45_smm/sm_07_7_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 8,
        title: "Part 8 – Program Integrity",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_08.zip",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106221935/http://www.cms.hhs.gov/manuals/pub45pdf/smm8t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041118225622/http://www.cms.hhs.gov/manuals/45_smm/sm_08_8_8001_to_8003with_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 9,
        title: "Part 9 – Utilization Control",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_09.zip",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222347/http://www.cms.hhs.gov/manuals/pub45pdf/smm9t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041212235359/http://www.cms.hhs.gov/manuals/45_smm/sm_09_9_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 11,
        title: "Part 11 – Medicaid Management Information System",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_11.zip",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222214/http://www.cms.hhs.gov/manuals/pub45pdf/smm11t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041212235810/http://www.cms.hhs.gov/manuals/45_smm/sm_11_11_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 13,
        title: "Part 13 – State Plan Procedures and Preprints",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_13.zip",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222106/http://www.cms.hhs.gov/manuals/pub45pdf/smm13t.pdf",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041212234952/http://www.cms.hhs.gov/manuals/45_smm/sm_13_13_toc.asp",
            date: ""
        },
        subsections: [
        ],
    },
    {
        id: 15,
        title: "Part 15 - Income and Eligibility Verification System",
        zip: {
            url: "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/p45_15.zip",
            date: ""
        },
        web: {
            url: "https://web.archive.org/web/20041212235650/http://www.cms.hhs.gov/manuals/45_smm/sm_15_15_toc.asp",
            date: ""
        },
        pdf: {
            url: "https://web.archive.org/web/20041106222351/http://www.cms.hhs.gov/manuals/pub45pdf/smm15t.pdf",
            date: ""
        },
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
                <div class="">
                    <p class="manual-page-description">
                        This page provides links to 
                        <a 
                            class="external"
                            target="_blank"
                            href="https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Paper-Based-Manuals-Items/CMS021927"
                        >
                        zipped Word documents from the CMS website</a>, which is the most complete version of the manual, 
                        along with links to convenient 
                        <a 
                            class="external"
                            target="_blank"
                            href="https://web.archive.org/web/20041212094406/http://www.cms.hhs.gov/manuals/45_smm/pub45toc.asp"
                        >
                        web pages</a> 
                        and 
                        <a
                            class="external"
                            target="_blank"
                            href="https://web.archive.org/web/20050204151206/http://www.cms.hhs.gov:80/manuals/pub45pdf/smmtoc.asp"
                        >
                        PDFs</a>
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
                                            <a v-if="section.zip?.url" :href="section.zip.url" target="_blank" class="link-btn">
                                                Word <span v-if="section.zip.date" class="date-stamp">({{ section.zip.date }})</span>
                                            </a>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.web?.url" :href="section.web.url" target="_blank" class="link-btn">
                                                Web <span v-if="section.web.date" class="date-stamp">({{ section.web.date }})</span>
                                            </a>
                                        </td>
                                        <td class="table__cell">
                                            <a v-if="section.pdf?.url" :href="section.pdf.url" target="_blank" class="link-btn">
                                                PDF <span v-if="section.pdf.date" class="date-stamp">({{ section.pdf.date }})</span>
                                            </a>
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
                                                <td class="table__cell">
                                                    <span v-if="sub.zip?.date" class="date-stamp">({{ sub.zip.date }})</span>
                                                </td>
                                                <td class="table__cell">
                                                    <a v-if="sub.web?.url" :href="sub.web.url" target="_blank" class="link-btn">
                                                        Web <span v-if="sub.web.date" class="date-stamp">({{ sub.web.date }})</span>
                                                    </a>
                                                </td>
                                                <td class="table__cell">
                                                    <a v-if="sub.pdf?.url" :href="sub.pdf.url" target="_blank" class="link-btn">
                                                        PDF <span v-if="sub.pdf.date" class="date-stamp">({{ sub.pdf.date }})</span>
                                                    </a>
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
                                                        <a v-if="nestedSub.web?.url" :href="nestedSub.web.url" target="_blank" class="link-btn">
                                                            Web <span v-if="nestedSub.web.date" class="date-stamp">({{ nestedSub.web.date }})</span>
                                                        </a>
                                                    </td>
                                                    <td class="table__cell">
                                                        <a v-if="nestedSub.pdf?.url" :href="nestedSub.pdf.url" target="_blank" class="link-btn">
                                                            PDF <span v-if="nestedSub.pdf.date" class="date-stamp">({{ nestedSub.pdf.date }})</span>
                                                        </a>
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
    vertical-align: top;
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

.date-stamp {
    font-size: 0.8em;
    color: #666;
    margin-left: 4px;
}

</style> 