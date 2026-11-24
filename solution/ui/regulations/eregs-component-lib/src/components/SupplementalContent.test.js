import { afterEach, beforeEach, describe, it, expect, vi } from "vitest";
import { shallowMount } from "@vue/test-utils";
import flushPromises from "flush-promises";

import SupplementalContent from "./SupplementalContent.vue";

describe("SupplementalContent", () => {
    beforeEach(() => {
        global.fetch = vi.fn((url) => {
            if (url.includes("/toc")) {
                return Promise.resolve({
                    ok: true,
                    status: 200,
                    text: () =>
                        Promise.resolve(
                            JSON.stringify([
                                {
                                    type: "section",
                                    identifier: ["433", "10"],
                                    children: [],
                                },
                                {
                                    type: "section",
                                    identifier: ["433", "11"],
                                    children: [],
                                },
                            ])
                        ),
                });
            }

            return Promise.resolve({
                ok: true,
                status: 200,
                text: () => Promise.resolve(JSON.stringify({ results: [], count: 0 })),
            });
        });
    });

    afterEach(() => {
        vi.clearAllMocks();
        window.history.replaceState({}, "", "/");
    });

    it("sends only title.part citation for the public call in the /full/ reader view", async () => {
        window.history.replaceState({}, "", "/42/431/full/");

        shallowMount(SupplementalContent, {
            props: {
                apiUrl: "/v3/",
                title: "42",
                part: "431",
                subparts: ["A", "B", "C"],
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls.some((url) => url.includes("/toc"))).toBe(false);
        expect(fetchedUrls).toContain(
            "/v3/resources/public?&citations=42.431&sort=-date&page_size=1000&page=1"
        );
    });

    it("sends subpart and section citations for the public call in a subpart reader view", async () => {
        window.history.replaceState({}, "", "/42/433/Subpart-A/");

        shallowMount(SupplementalContent, {
            props: {
                apiUrl: "/v3/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls).toContain("/v3/title/42/part/433/subpart/A/toc");
        expect(fetchedUrls).toContain(
            "/v3/resources/public?&citations=42.433.A&citations=42.433.10&citations=42.433.11&sort=-date&page_size=1000&page=1"
        );
    });

    it("falls back to title.part citation when /full/ reader view has no subparts", async () => {
        window.history.replaceState({}, "", "/42/433/full/");

        shallowMount(SupplementalContent, {
            props: {
                apiUrl: "/v3/",
                title: "42",
                part: "433",
                subparts: [],
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls.some((url) => url.includes("/toc"))).toBe(false);
        expect(fetchedUrls).toContain(
            "/v3/resources/public?&citations=42.433&sort=-date&page_size=1000&page=1"
        );
    });
});
