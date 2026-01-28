import { beforeEach, afterEach, describe, it, expect, vi } from "vitest";

import {
    getCombinedContent,
    getContentWithoutQuery,
    getContextBanners,
    getExternalCategories,
    getGovInfoLinks,
    getGranularCounts,
    getInternalCategories,
    getInternalDocs,
    getLastUpdatedDates,
    getParts,
    getRecentResources,
    getRegSearchResults,
    getSemanticSearchResults,
    getStatutes,
    getStatutesActs,
    getSubjects,
    getChildTOC,
    getSynonyms,
    getTitles,
    getVersionHistory,
    throwGenericError,
} from "utilities/api.js";

import flushPromises from "flush-promises";

const fetchGetBoilerplate = {
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

const fetchPostBoilerplate = {
    cache: "no-cache",
    headers: {
        Accept: "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": null,
    },
    method: "POST",
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
    describe("getChildTOC", () => {
        it("is called with proper param string", async () => {
            await getChildTOC({
                apiUrl: "http://localhost:9000/",
                title: "42",
                part: "431",
                subPart: "10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/part/431/version/latest/subpart/10/toc",
                fetchGetBoilerplate
            );
        });
        it("is called without subPart param", async () => {
            await getChildTOC({
                apiUrl: "http://localhost:9000/",
                title: "42",
                part: "431",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/part/431/version/latest/toc",
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
            );
            expect(fetch).toHaveBeenNthCalledWith(
                2,
                "http://localhost:9000/title/45/parts",
                fetchGetBoilerplate
            );
        });
    });
    describe("getRecentResources", () => {
        it("is called with type = rules", async () => {
            await getRecentResources({
                apiUrl: "http://localhost:9000/",
                args: {
                    categories: "1",
                    page: 1,
                    pageSize: 3,
                    type: "rules",
                },
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/public/federal_register_links?page=1&page_size=3",
                fetchGetBoilerplate
            );
        });
        it("is called with type != rules", async () => {
            await getRecentResources({
                apiUrl:  "http://localhost:9000/",
                args: {
                    categories: "&categories=1",
                    page: 2,
                    pageSize: 5,
                    type: "not_rules",
                },
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/public/links?page=2&page_size=5&categories=1",
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
            );
        });
    });
    describe("getSemanticSearchResults", () => {
        it("is called with proper param string", async () => {
            const data = "q=test";
            const fetchBoilerplateWithData = {...fetchPostBoilerplate, body: data };

            await getSemanticSearchResults({
                apiUrl: "http://localhost:9000/",
                data,
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/",
                fetchBoilerplateWithData
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
                fetchGetBoilerplate
            );
        });
        it("is called without requestParams param string", async () => {
            await getCombinedContent({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/",
                fetchGetBoilerplate
            );
        });
    });
    describe("getGranularCounts", () => {
        it("is called with requestParams param string", async () => {
            const data = "q=test";
            const fetchBoilerplateWithData = {...fetchPostBoilerplate, body: data };

            await getGranularCounts({
                apiUrl: "http://localhost:9000/",
                data,
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/counts",
                fetchBoilerplateWithData
            );
        });
        it("is called without requestParams param string", async () => {
            const fetchBoilerplateWithData = {...fetchPostBoilerplate, body: {} };

            await getGranularCounts({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/content-search/counts",
                fetchBoilerplateWithData
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
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
                fetchGetBoilerplate
            );
        });
        it("is called without requestParams param string or docType", async () => {
            await getContentWithoutQuery({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/",
                fetchGetBoilerplate
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
                fetchGetBoilerplate
            );
        });
        it("is called without requestParams param string", async () => {
            await getInternalDocs({
                apiUrl: "http://localhost:9000/",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/internal",
                fetchGetBoilerplate
            );
        });
    });
    describe("getContextBanners", () => {
        it("is called with proper param string", async () => {
            await getContextBanners({
                apiUrl: "http://localhost:9000/",
                requestParams: "title=42&part=433&section=433.10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/resources/context-banners?title=42&part=433&section=433.10",
                fetchGetBoilerplate
            );
        });
    });
    describe("getVersionHistory", () => {
        it("is called with proper param string", async () => {
            await getVersionHistory({
                apiUrl: "http://localhost:9000/",
                title: "42",
                part: "431",
                section: "10",
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/part/431/versions/section/10",
                fetchGetBoilerplate
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
