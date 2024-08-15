import { describe, it, expect } from "vitest";

import PolicyResults from "./PolicyResults.vue";

const MOCK_RESULTS = [
    {
        resource: {
            type: "internal_file",
            title: "this is a document name string",
        },
        name_headline: "this is a document name headline",
        summary_string: "this is a summary string",
        summary_headline:
            "this <span class='search-highlight'>is</span> a summary headline",
        file_name: "index_one.docx",
        content_headline:
            "this <span class='search-highlight'>is</span> a content headline",
        url: "url",
    },
];

describe("addSurroundingEllipses", () => {
    it("adds ellipses to the beginning and end of a string", async () => {
        expect(
            PolicyResults.addSurroundingEllipses(
                "this <span class='search-highlight'>is</span> a string"
            )
        ).toBe("...this <span class='search-highlight'>is</span> a string...");
    });

    it("does NOT add ellipses to the beginning and end of a string", async () => {
        expect(PolicyResults.addSurroundingEllipses("this is a string")).toBe(
            "this is a string"
        );
    });
});

describe("getResultLinkText", () => {
    it("/content_search internal result", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[0])).toBe(
            "<span class='result__link--label'>this is a document name headline</span>"
        );
    });
    it("/resources/internal result", async () => {
        const result = {
            type: "internal_file",
            cfr_citations: [],
            subjects: [],
            document_id: "docID",
            title: "this is a document name string",
            date: "2024-10-10",
            url: "",
            related_resources: null,
            summary: "This is the summary for the test text file",
            file_name: "test.txt",
            file_type: "",
            uid: "a4e00982-4944-4a8d-8dd9-e5d2caa11f51",
        };
        expect(PolicyResults.getResultLinkText(result)).toBe(
            "<span class='result__link--label'>this is a document name string</span>"
        );
    });
    it("/content-search external result", async () => {
        const result = {
            name_headline: "",
            summary_headline:
                "this <span class='search-highlight'>is</span> a summary headline",
            content_headline: "",
            resource: {
                type: "public_link",
                category: {},
                cfr_citations: [],
                subjects: [],
                document_id: "",
                title: "",
                date: "2021-06-28",
                url:
                    "https://innovation.cms.gov/data-and-reports/2021/sim-rd2-test-final-appendix",
                related_resources: null,
            },
            reg_text: null,
        };
        expect(PolicyResults.getResultLinkText(result)).toBe(
            "<span class='result__link--label'>this <span class='search-highlight'>is</span> a summary headline</span>"
        );
    });
    it("/resources/public (external) result", async () => {
        const result = {
            type: "federal_register_link",
            approved: true,
            category: {},
            cfr_citations: [],
            subjects: [],
            document_id: "00 FR 00000",
            title: "this is a title",
            date: "2024-07-23",
            url: "https://www.federalregister.gov/",
            related_resources: null,
            docket_numbers: ["TEST-GROUP-000"],
            document_number: "00-0000",
            correction: false,
            withdrawal: false,
            action_type: "RFI",
        };
        expect(PolicyResults.getResultLinkText(result)).toBe(
            "<span class='result__link--label'>this is a title</span>"
        );
    });
});

describe("getResultSnippet", () => {
    it("is internal and has a content_headline and summary_headline with a search result", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[1])).toBe(
            "...this <span class='search-highlight'>is</span> a content headline..."
        );
    });
    it("is internal and has a summary_headline WITHOUT a search result", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[7])).toBe(
            "this is a summary headline"
        );
    });
    it("is internal and has a content_headline and a summary_string but NOT a summary_headline", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[6])).toBe(
            "...this <span class='search-highlight'>is</span> a content headline..."
        );
    });
    it("is internal and does NOT have a summary_headline or _string, but has a content_headline with a search result", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[0])).toBe(
            "...this <span class='search-highlight'>is</span> a content headline..."
        );
    });
});

describe("showResultSnippet", () => {
    it("is internal and has a summary_headline", async () => {
        expect(PolicyResults.showResultSnippet(MOCK_RESULTS[1])).toBe(true);
    });
    it("is internal and does NOT have a summary_headline or summary_string or content_headline", async () => {
        expect(PolicyResults.showResultSnippet(MOCK_RESULTS[2])).toBe(false);
    });
    it("is external and has a content_headline", async () => {
        expect(PolicyResults.showResultSnippet(MOCK_RESULTS[3])).toBe(true);
    });
    it("is external and does NOT have a content_headline or content_string", async () => {
        expect(PolicyResults.showResultSnippet(MOCK_RESULTS[5])).toBe(false);
    });
});
