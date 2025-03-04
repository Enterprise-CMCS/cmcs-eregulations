import { describe, it, expect } from "vitest";

import RelatedRuleList from "./RelatedRuleList.vue";

describe("Related Rule List", () => {
    it("correctly returns a citation from a rule", () => {
        const rule1 = {
            citation: "42 CFR 123.456",
            document_id: "XYZ-890",
        };

        const rule2 = {
            document_id: "ABC-123",
        };

        expect(RelatedRuleList.citation(rule1)).toBe("42 CFR 123.456");
        expect(RelatedRuleList.citation(rule2)).toBe("ABC-123");

    });

    it("correctly returns a url from a rule", () => {
        const rule1 = {
            html_url: "https://html.com",
            url: "https://url.com",
        };

        const rule2 = {
            url: "https://url.com",
        };

        expect(RelatedRuleList.html_url(rule1)).toBe("https://html.com");
        expect(RelatedRuleList.html_url(rule2)).toBe("https://url.com");
    });

    it("correctly returns a publication date from a rule", () => {
        const rule1 = {
            publication_date: "2021-01-01",
            date: "2021-01-01T00:00:00Z",
        };

        const rule2 = {
            date: "2021-01-01T00:00:00Z",
        };

        expect(RelatedRuleList.publication_date(rule1)).toBe("2021-01-01");
        expect(RelatedRuleList.publication_date(rule2)).toBe("2021-01-01T00:00:00Z");
    });

    it("correctly returns a title from a rule", () => {
        const rule1 = {
            title: "Title 1",
            description: "XYZ-890",
        };

        const rule2 = {
            description: "ABC-123",
        };

        expect(RelatedRuleList.ruleTitle(rule1)).toBe("Title 1");
        expect(RelatedRuleList.ruleTitle(rule2)).toBe("ABC-123");
    });
});
