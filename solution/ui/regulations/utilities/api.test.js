import { describe, it, expect, vi } from "vitest";

import {
    getLastUpdatedDates,
    getRecentResources,
    getRegSearchResults,
    getSubpartTOC,
    getSynonyms,
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
});
