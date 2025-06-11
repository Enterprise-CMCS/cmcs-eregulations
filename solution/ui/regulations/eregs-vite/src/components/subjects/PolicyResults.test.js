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
    {
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
    },
    {
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
            url: "https://innovation.cms.gov/data-and-reports/2021/sim-rd2-test-final-appendix",
            related_resources: null,
        },
        reg_text: null,
    },
    {
        name_headline: "",
        summary_headline:
            "this <span class='search-highlight'>is</span> a summary headline",
        content_headline:
            "this <span class='search-highlight'>is</span> a content headline",
        resource: {
            type: "public_link",
            category: {},
            cfr_citations: [],
            subjects: [],
            document_id: "",
            title: "",
            date: "2021-06-28",
            url: "https://innovation.cms.gov/data-and-reports/2021/sim-rd2-test-final-appendix",
            related_resources: null,
        },
        reg_text: null,
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

describe("getParentCategoryName", () => {
    const itemCategory = {
        parent: 1,
    };

    const categoriesArr = [
        {
            id: 1,
            name: "Statutes",
            description: "",
            order: 200,
            show_if_empty: false,
            is_fr_link_category: false,
            type: "",
            subcategories: [],
            categoryType: "categories",
            catIndex: 0,
        },
    ];
    it("returns null if no itemCategory", async () => {
        expect(
            PolicyResults.getParentCategoryName({
                itemCategory: "",
            })
        ).toBe(null);
    });

    it("returns the parent category name", async () => {
        expect(
            PolicyResults.getParentCategoryName({
                itemCategory,
                categoriesArr,
            })
        ).toBe("Statutes");
    });
});

describe("getResultLinkText", () => {
    const cs_internal_1 = {
        type: "internal",
        name_headline: "this is a name_headline field",
        title: "this is a title field",
    };

    it("/content_search internal result 1", async () => {
        expect(PolicyResults.getResultLinkText(cs_internal_1)).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a name_headline field</span><span class='spacer__span'> </span></span>"
        );
    });

    const cs_internal_with_url_1 = {
        type: "internal",
        name_headline: "this is a name_headline field",
        title: "this is a title field",
        url: "https://www.example.com/file.pdf",
        uid: "12345",
    };

    it("/content_search internal result with url 1", async () => {
        expect(PolicyResults.getResultLinkText(cs_internal_with_url_1)).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a name_headline field</span><span class='spacer__span'> </span><span data-testid='download-chip-12345' class='result__link--file-type'>PDF</span><span class='spacer__span'>&nbsp</span><span class='result__link--domain'>example.com</span></span>"
        );
    });

    const cs_internal_2 = {
        type: "internal",
        name_headline: "",
        title: "this is a title field",
    };

    it("/content_search internal result 2", async () => {
        expect(PolicyResults.getResultLinkText(cs_internal_2)).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a title field</span><span class='spacer__span'> </span></span>"
        );
    });

    it("/resources/internal result", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[1])).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a document name string</span><span class='spacer__span'> </span><span data-testid='download-chip-a4e00982-4944-4a8d-8dd9-e5d2caa11f51' class='result__link--file-type'>TXT</span></span>"
        );
    });

    const cs_external_1 = {
        type: "external",
        summary_headline: "this is a summary_headline field",
        name_headline: "this is a name_headline field",
        title: "this is a title field",
    };

    it("/content-search external result", async () => {
        expect(PolicyResults.getResultLinkText(cs_external_1)).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a summary_headline field</span><span class='spacer__span'> </span></span>"
        );
    });

    const cs_external_2 = {
        type: "external",
        summary_headline: "",
        name_headline: "this is a name_headline field",
    };

    it("/content-search external result", async () => {
        expect(PolicyResults.getResultLinkText(cs_external_2)).toBe(
            "<span class='result__link--label'><span class='result__label--title'>this is a name_headline field</span><span class='spacer__span'> </span></span>"
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
            "<span class='result__link--label'><span class='result__label--title'>this is a title</span><span class='spacer__span'> </span><span class='spacer__span'>&nbsp</span><span class='result__link--domain'>federalregister.gov</span></span>"
        );
    });
});

describe("getResultSnippet", () => {
    const cs_internal_1 = {
        type: "internal",
        content_headline:
            "this is a <span class='search-highlight'>content_headline</span>",
    };

    it("/content-search internal result with both content_headline", async () => {
        expect(PolicyResults.getResultSnippet(cs_internal_1)).toBe(
            "...this is a <span class='search-highlight'>content_headline</span>..."
        );
    });

    const cs_internal_2 = {
        type: "internal",
        content_headline: "",
        summary_headline:
            "this is a <span class='search-highlight'>summary_headline</span>",
    };

    it("/content-search internal result with summary_headline", async () => {
        expect(PolicyResults.getResultSnippet(cs_internal_2)).toBe(
            "...this is a <span class='search-highlight'>summary_headline</span>..."
        );
    });

    const cs_internal_3 = {
        type: "internal",
        content_headline: "",
        summary_headline: "",
        summary_string: "this is a summary_string",
    };

    it("/content-search internal result with summary_string", async () => {
        expect(PolicyResults.getResultSnippet(cs_internal_3)).toBe(
            "this is a summary_string"
        );
    });

    const cs_internal_4 = {
        type: "internal",
        content_headline: "",
        summary_headline: "",
        summary_string: "",
        summary: "this is a summary",
    };

    it("/content-search internal result with summary", async () => {
        expect(PolicyResults.getResultSnippet(cs_internal_4)).toBe(
            "this is a summary"
        );
    });

    const cs_external_1 = {
        type: "external",
        content_headline:
            "this is a <span class='search-highlight'>content_headline</span>",
        content_string: "this is a content_string",
    };

    it("/content-search external result with content_headline", async () => {
        expect(PolicyResults.getResultSnippet(cs_external_1)).toBe(
            "...this is a <span class='search-highlight'>content_headline</span>..."
        );
    });

    const cs_external_2 = {
        type: "external",
        content_headline: "",
        content_string: "this is a content_string",
    };

    it("/content-search external result with content_string", async () => {
        expect(PolicyResults.getResultSnippet(cs_external_2)).toBe(
            "this is a content_string"
        );
    });

    it("/resources/internal with a summary", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[1])).toBe(
            "This is the summary for the test text file"
        );
    });
});

describe("showResultSnippet", () => {
    const cs_internal_1 = {
        type: "internal",
        content_headline:
            "this is a <span class='search-highlight'>content_headline</span>",
    };

    it("/content-search internal result and has a content_headline", async () => {
        expect(PolicyResults.showResultSnippet(cs_internal_1)).toBe(true);
    });

    const cs_internal_2 = {
        type: "internal",
        content_headline: "",
    };

    it("/content-search internal result and does not have headlines or summaries", async () => {
        expect(PolicyResults.showResultSnippet(cs_internal_2)).toBe(false);
    });

    it("/resources/internal result and has a summary_headline", async () => {
        expect(PolicyResults.showResultSnippet(MOCK_RESULTS[1])).toBe(true);
    });

    it("/resources/internal and does NOT have a summary_headline or summary_string or content_headline", async () => {
        const result = {
            type: "internal_file",
            cfr_citations: [],
            subjects: [],
            document_id: "docID",
            title: "this is a document name string",
            date: "2024-10-10",
            url: "",
            related_resources: null,
            summary: "",
            file_name: "test.txt",
            file_type: "",
            uid: "a4e00982-4944-4a8d-8dd9-e5d2caa11f51",
        };
        expect(PolicyResults.showResultSnippet(result)).toBe(false);
    });

    const cs_external_1 = {
        type: "external",
        content_headline:
            "this is a <span class='search-highlight'>content_headline</span>",
    };

    it("/content-search external and has a content_headline", async () => {
        expect(PolicyResults.showResultSnippet(cs_external_1)).toBe(true);
    });

    const cs_external_2 = {
        type: "external",
        content_headline: "",
    };

    it("/content-search external and does NOT have a content_headline", async () => {
        expect(PolicyResults.showResultSnippet(cs_external_2)).toBe(false);
    });
});
