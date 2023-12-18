import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import PolicyResults from "./PolicyResults.vue";

const MOCK_RESULTS = [
    {
        resource_type: "internal",
        doc_name_string: "this is a document name string",
        document_name_headline: "this is a document name headline",
        summary_string: null,
        summary_headline: null,
        file_name_string: "index_zero.docx",
        content_string: "this is a content string",
        content_headline: "this is a content headline",
        url: "url",
    },
    {
        resource_type: "internal",
        doc_name_string: "this is a document name string",
        document_name_headline: "this is a document name headline",
        summary_string: "this is a summary string",
        summary_headline: "this is a summary headline",
        file_name_string: "index_one.docx",
        content_string: "this is a content string",
        content_headline: "this is a content headline",
        url: "url",
    },
    {
        resource_type: "internal",
        doc_name_string: "this is a document name string",
        document_name_headline: null,
        summary_string: null,
        summary_headline: null,
        file_name_string: "index_two.docx",
        url: "url",
    },
    {
        resource_type: "external",
        summary_string: "this is a summary string",
        summary_headline: "this is a summary headline",
        file_name_string: "index_three.docx",
        content_string: "this is a content string",
        content_headline: "this is a content headline",
        url: "url",
    },
    {
        resource_type: "external",
        summary_string: "this is a summary string",
        summary_headline: null,
        file_name_string: "index_four.pdf",
        content_string: "this is a content string",
        content_headline: null,
        url: "url",
    },
    {
        resource_type: "external",
        summary_string: "this is a summary string",
        summary_headline: "this is a summary headline",
        file_name_string: "index_five.docx",
        url: "url",
    },
];

describe("getFileTypeButton", () => {
    it("is a DOCX file", async () => {
        expect(PolicyResults.getFileTypeButton(MOCK_RESULTS[0])).toBe(
            "<span data-testid='download-chip-url' class='result__link--file-type'>Download DOCX</span>"
        );
    });

    it("is a PDF file", async () => {
        expect(PolicyResults.getFileTypeButton(MOCK_RESULTS[4])).toBe("");
    });
});

describe("getResultLinkText", () => {
    it("is internal and has a document_name_headline", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[1])).toBe(
            "<span class='result__link--label'>this is a document name headline</span>"
        );
    });
    it("is internal and does NOT have a document_name_headline", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[2])).toBe(
            "<span class='result__link--label'>this is a document name string</span>"
        );
    });
    it("is external and has a summary_headline", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[3])).toBe(
            "<span class='result__link--label'>this is a summary headline</span>"
        );
    });
    it("is external and does NOT have a summary_headline", async () => {
        expect(PolicyResults.getResultLinkText(MOCK_RESULTS[4])).toBe(
            "<span class='result__link--label'>this is a summary string</span>"
        );
    });
});

describe("getResultSnippet", () => {
    it("is internal and has a summary_headline", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[1])).toBe(
            "...this is a summary headline..."
        );
    });
    it("is internal and does NOT have a summary_headline or _string, but has a content_headline", async () => {
        expect(PolicyResults.getResultSnippet(MOCK_RESULTS[0])).toBe(
            "...this is a content headline..."
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
