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
            "https://www.medicaid.gov/search-gsc?&gsc.sort=#gsc.tab=0&gsc.q=test%20query&gsc.sort="
        );
    });

    it("makes the expected US Code link", () => {
        expect(SearchContinueResearch.makeUsCodeLink("test query")).toBe(
            "https://uscode.house.gov/search.xhtml?edition=prelim&searchString=%28test%20query%29+AND+%28%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2819%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2821%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2818%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2816%29%29+OR+%28title%3A%2842%29+AND+chapter%3A%287%29+AND+subchapter%3A%2811%29%29%29&pageNumber=1&itemsPerPage=100&sortField=RELEVANCE&displayType=CONTEXT&action=search&q=dGVzdCBxdWVyeQ%3D%3D%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7Ctrue%7C%5B42%3A%3A%3A%3A7%3A19%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A21%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A18%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A16%3A%3A%3Atrue%3A%3B42%3A%3A%3A%3A7%3A11%3A%3A%3Atrue%3A%5D%7C%5BQWxsIEZpZWxkcw%3D%3D%3A%5D"
        );
    });
});
