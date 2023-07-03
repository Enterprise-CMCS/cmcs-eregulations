import { houseGovUrl, statuteCompilationUrl, usCodeUrl, ssaGovUrl } from "../utils/urlMethods.js";

const ssaSchema = [
    {
        header: {
            title: "Statute Citation",
            primary: true,
        },
        body: {
            title: (statute) => `SSA Section ${statute.section}`,
            label: (statute) => `${statute.title} U. S. C. ${statute.usc}`,
            name: (statute) => `${statute.name}`,
            primary: true,
        },
    },
    {
        header: {
            title: "House.gov",
            secondary: true,
            subtitles: ["Web Page", "Effective Jun 2023"],
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
            title: "Statute Compilation",
            secondary: true,
            subtitles: ["PDF Document", "Amended Dec 2022"],
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
            title: "US Code Annual",
            secondary: true,
            subtitles: ["PDF Document", "Effective Jan 2022"],
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
            title: "SSA.gov",
            secondary: true,
            subtitles: ["Web Page", "Amended Dec 2019"],
        },
        body: {
            url: (statute) => ssaGovUrl(statute),
            text: (statute) => `${statute.section}`,
            type: "external",
            secondary: true,
        },
    },
];

export {
    ssaSchema,
};
