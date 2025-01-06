import { describe, it, expect, vi } from "vitest";

import {
    getCombinedContent,
    getContentWithoutQuery,
    getExternalCategories,
    getLastUpdatedDates,
    getGovInfoLinks,
    getGranularCounts,
    getInternalCategories,
    getInternalDocs,
    getParts,
    getRecentResources,
    getRegSearchResults,
    getStatutes,
    getStatutesActs,
    getSubjects,
    getSubpartTOC,
    getSynonyms,
    getTitles,
    throwGenericError,
} from "utilities/api.js";

import flushPromises from "flush-promises";

const fetchBoilerplate = {
    cache: "no-cache",
    headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
    },
    method: "GET",
    mode: "cors",
    params: undefined,
    redirect: "follow",
};

describe("api.js", () => {
    beforeEach(() => {
        // mock global fetch for our single async call
        global.fetch = vi.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve("fetch response"),
            })
        );
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    describe("getSubpartTOC", () => {
        it("is called with proper param string", async () => {
            await getSubpartTOC({
                apiUrl: "http://localhost:9000/",
                title: "42",
                part: "431",
                subPart: "10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/part/431/version/latest/subpart/10/toc",
                fetchBoilerplate
            );
        });
    });
    describe("getSynonyms", () => {
        it("is called with proper param string", async () => {
            await getSynonyms({
                apiUrl: "http://localhost:9000/",
                query: "test query",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/synonyms?q=test%20query",
                fetchBoilerplate
            );
        });
    });
    describe("getRegSearchResults", () => {
        it("is called with proper param string", async () => {
            await getRegSearchResults({
                apiUrl: "http://localhost:9000/",
                q: "test query",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/search?q=test%20query&paginate=true&page_size=100&page=1",
                fetchBoilerplate
            );
        });
    });
    describe("getLastUpdatedDates", () => {
        it("is called with proper param string", async () => {
            await getLastUpdatedDates({
                apiUrl: "http://localhost:9000/",
                titles: ["42", "45"],
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledTimes(2);
            expect(fetch).toHaveBeenNthCalledWith(
                1,
                "http://localhost:9000/title/42/parts",
                fetchBoilerplate
            );
            expect(fetch).toHaveBeenNthCalledWith(
                2,
                "http://localhost:9000/title/45/parts",
                fetchBoilerplate
            );
        });
    });
    describe("getRecentResources", () => {
        it("is called with type = rules", async () => {
            await getRecentResources("http://localhost:9000/", {
                categories: "1",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/public/federal_register_links?page=1&page_size=3",
                fetchBoilerplate
            );
        });
        it("is called with type != rules", async () => {
            await getRecentResources("http://localhost:9000/", {
                categories: "&categories=1",
                page: 2,
                pageSize: 5,
                type: "not_rules",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/public/links?page=2&page_size=5&categories=1",
                fetchBoilerplate
            );
        });
    });
    describe("getGovInfoLinks", () => {
        it("is called with proper param string", async () => {
            await getGovInfoLinks({
                apiUrl: "http://localhost:9000/",
                filterParams: {
                    title: "42",
                    part: "431",
                    section: "10",
                },
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/part/431/history/section/10",
                fetchBoilerplate
            );
        });
    });
    describe("getTitles", () => {
        it("is called with proper param string", async () => {
            await getTitles({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/titles",
                fetchBoilerplate
            );
        });
    });
    describe("getParts", () => {
        it("is called with proper param string", async () => {
            await getParts({
                apiUrl: "http://localhost:9000/",
                title: "42",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/parts",
                fetchBoilerplate
            );
        });
    });
    describe("getStatutesActs", () => {
        it("is called with proper param string", async () => {
            await getStatutesActs({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/acts",
                fetchBoilerplate
            );
        });
    });
    describe("getStatutes", () => {
        it("is called with default params", async () => {
            await getStatutes({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/statutes?act=Social%20Security%20Act&title=19",
                fetchBoilerplate
            );
        });
        it("is called properly with all named params present", async () => {
            await getStatutes({
                apiUrl: "http://localhost:9000/",
                act: "test act",
                title: "42",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/statutes?act=test%20act&title=42",
                fetchBoilerplate
            );
        });
    });
    describe("getSubjects", () => {
        it("is called with proper param string", async () => {
            await getSubjects({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/subjects?page_size=1000",
                fetchBoilerplate
            );
        });
    });
    describe("getInternalCategories", () => {
        it("is called with proper param string", async () => {
            await getInternalCategories({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/internal/categories?page_size=1000",
                fetchBoilerplate
            );
        });
    });
    describe("getExternalCategories", () => {
        it("is called with proper param string", async () => {
            await getExternalCategories({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/public/categories?page_size=1000",
                fetchBoilerplate
            );
        });
    });
    describe("getCombinedContent", () => {
        it("is called with requestParams param string", async () => {
            await getCombinedContent({
                apiUrl: "http://localhost:9000/",
                requestParams: "locations=42.431.10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/?locations=42.431.10",
                fetchBoilerplate
            );
        });
        it("is called without requestParams param string", async () => {
            await getCombinedContent({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/",
                fetchBoilerplate
            );
        });
    });
    describe("getGranularCounts", () => {
        it("is called with requestParams param string", async () => {
            await getGranularCounts({
                apiUrl: "http://localhost:9000/",
                requestParams: "locations=42.431.10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/counts?locations=42.431.10",
                fetchBoilerplate
            );
        });
        it("is called without requestParams param string", async () => {
            await getGranularCounts({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/counts",
                fetchBoilerplate
            );
        });
    });
    describe("getContentWithoutQuery", () => {
        it("is called with requestParams param string", async () => {
            await getContentWithoutQuery({
                apiUrl: "http://localhost:9000/",
                requestParams: "locations=42.431.10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/?locations=42.431.10",
                fetchBoilerplate
            );
        });
        it("is called with docType", async () => {
            await getContentWithoutQuery({
                apiUrl: "http://localhost:9000/",
                docType: "test",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/test",
                fetchBoilerplate
            );
        });
        it("is called with requestParams param string and docType", async () => {
            await getContentWithoutQuery({
                apiUrl: "http://localhost:9000/",
                requestParams: "locations=42.431.10",
                docType: "test",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/test?locations=42.431.10",
                fetchBoilerplate
            );
        });
        it("is called without requestParams param string or docType", async () => {
            await getContentWithoutQuery({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/",
                fetchBoilerplate
            );
        });
    });
    describe("getInternalDocs", () => {
        it("is called with requestParams param string", async () => {
            await getInternalDocs({
                apiUrl: "http://localhost:9000/",
                requestParams: "locations=42.431.10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/internal?locations=42.431.10",
                fetchBoilerplate
            );
        });
        it("is called without requestParams param string", async () => {
            await getInternalDocs({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/internal",
                fetchBoilerplate
            );
        });
    });
    describe("throwGenericError", () => {
        it("throws an error", async () => {
            expect(async () => await throwGenericError()).rejects.toThrow(
                "Contrived error"
            );
        });
    });
});
