import {
    houseGovUrl,
    ssaGovUrl,
    statuteCompilationUrl,
    usCodeUrl,
} from "../utils/urlMethods.js";
import { getDateLabel } from "../utils/dateMethods.js";

// placeholder for future schema
const acaSchema = [
    {
        header: {
            title: "Primary Column",
            primary: true,
        },
        body: {
            title: "ACA Title",
            label: "ACA Label",
            name: "ACA Name",
            primary: true,
        },
    },
    {
        header: {
            title: "Secondary Column",
            secondary: true,
            subtitles: ["Subtitle One", "Subtitle Two"],
        },
        body: {
            url: "Link href",
            text: "Link text",
            type: "external", // or "pdf"
            secondary: true,
        },
    },
];

const ssaSchema = [
    {
        header: {
            title: "Statute Citation",
            primary: true,
        },
        body: {
            title: (statute) => `Section ${statute.section}`,
            label: (statute) => `${statute.title} U.S.C. ${statute.usc}`,
            name: (statute) => `${statute.name}`,
            primary: true,
        },
    },
    {
        header: {
            testId: "house-gov-link",
            title: "US Code House.gov",
            secondary: true,
            subtitles: [
                (columnDates) =>
                    getDateLabel(columnDates?.us_code_house_gov ?? {}),
            ],
            learnMoreUrl: "https://uscode.house.gov/",
        },
        body: {
            url: (statute) => houseGovUrl(statute),
            text: (statute) => `${statute.usc}`,
            type: "external",
            secondary: true,
        },
    },
    {
        header: {
            testId: "statute-compilation-link",
            title: "Statute Compilation",
            secondary: true,
            subtitles: [
                (columnDates) =>
                    getDateLabel(columnDates?.statute_compilation ?? {}),
            ],
            learnMoreUrl: "https://www.govinfo.gov/app/collection/comps/",
        },
        body: {
            url: (statute) => statuteCompilationUrl(statute),
            text: (statute) => `Title ${statute.statute_title_roman}`,
            type: "pdf",
            secondary: true,
        },
    },
    {
        header: {
            testId: "us-code-annual-link",
            title: "US Code Annual",
            secondary: true,
            subtitles: [
                (columnDates) =>
                    getDateLabel(columnDates?.us_code_annual ?? {}),
            ],
            learnMoreUrl: "https://www.govinfo.gov/app/collection/uscode",
        },
        body: {
            url: (statute) => usCodeUrl(statute),
            text: (statute) => `${statute.usc}`,
            type: "pdf",
            secondary: true,
        },
    },
    {
        header: {
            testId: "ssa-gov-link",
            title: "SSA.gov Compilation",
            secondary: true,
            subtitles: [
                (columnDates) =>
                    getDateLabel(columnDates?.ssa_gov_compilation ?? {}),
            ],
            learnMoreUrl: "https://www.ssa.gov/OP_Home/ssact/ssact.htm",
        },
        body: {
            url: (statute) => ssaGovUrl(statute),
            text: (statute) => `${statute.section}`,
            type: "external",
            secondary: true,
        },
    },
];

export { acaSchema, ssaSchema };
