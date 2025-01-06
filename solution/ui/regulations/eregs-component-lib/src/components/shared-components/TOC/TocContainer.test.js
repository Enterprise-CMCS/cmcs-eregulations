import { describe, it, expect, vi } from "vitest";
import { ref } from "vue";

import TocContainer from "./TocContainer.vue";

import flushPromises from "flush-promises";

describe("Toc Container", () => {
    afterEach(() => {
        vi.clearAllMocks();
    });
    describe("getTitlesArray", () => {
        it("should properly format titles", async () => {
            const titles = ref([]);
            TocContainer.getTitlesArray({
                apiUrl: "http://localhost:9000/",
                titles,
            });
            await flushPromises();
            expect(titles.value).toEqual(["Title 42", "Title 45"]);
        });
    });

    describe("getTOCs", () => {
        it("should properly format TOCs", async () => {
            // mock global fetch for our single async call
            global.fetch = vi.fn(() =>
                Promise.resolve({
                    json: () => Promise.resolve("TOC response"),
                })
            );
            const TOCs = ref([]);
            TocContainer.getTOCs({
                apiUrl: "http://localhost:9000/",
                titlesArr: ["42"],
                TOCs,
            });
            await flushPromises();
            expect(fetch).toHaveBeenCalledWith(
                "http://localhost:9000/title/42/toc",
                {
                    cache: "no-cache",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                    method: "GET",
                    mode: "cors",
                    params: undefined,
                    redirect: "follow",
                }
            );
        });
    });
});
