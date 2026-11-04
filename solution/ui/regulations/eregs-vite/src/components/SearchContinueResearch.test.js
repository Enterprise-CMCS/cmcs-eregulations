import { describe, it, expect } from "vitest";

import SearchContinueResearch from "./SearchContinueResearch.vue";

describe("Search Continue Research", () => {
    it("correctly determines if a query string has spaces", () => {
        expect(SearchContinueResearch.hasSpaces("test")).toBe(false);
        expect(SearchContinueResearch.hasSpaces("test query")).toBe(true);
    });

    it("correctly determines if a query has quotes", () => {
        expect(SearchContinueResearch.hasQuotes("test")).toBe(false);
        expect(SearchContinueResearch.hasQuotes('"test"')).toBe(true);
        expect(SearchContinueResearch.hasQuotes("'test'")).toBe(true);
    });

    it("makes the expected ECFR link", () => {
        expect(
            SearchContinueResearch.makeEcfrLink({
                query: "test query",
                title: 42,
            })
        ).toBe(
            "https://www.ecfr.gov/search?search[hierarchy][title]=42&search[query]=test%20query"
        );
    });

    it("makes the expected Federal Register link", () => {
        expect(
            SearchContinueResearch.makeFederalRegisterLink("test query")
        ).toBe(
            "https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=test%20query"
        );
    });

    it("makes the expected Medicaid.gov link", () => {
        expect(SearchContinueResearch.makeMedicaidGovLink("test query")).toBe(
            "https://www.medicaid.gov/search/content?keys=test%20query"
        );
    });
});
