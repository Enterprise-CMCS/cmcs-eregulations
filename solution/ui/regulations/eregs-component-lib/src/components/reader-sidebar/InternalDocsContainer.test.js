import { afterEach, beforeEach, describe, it, expect, vi } from "vitest";
import { shallowMount } from "@vue/test-utils";
import flushPromises from "flush-promises";

import InternalDocsContainer from "./InternalDocsContainer.vue";

describe("InternalDocsContainer", () => {
    let nodeListScript;

    beforeEach(() => {
        nodeListScript = document.createElement("script");
        nodeListScript.id = "node_list";
        nodeListScript.type = "application/json";
        nodeListScript.textContent = JSON.stringify({
            subparts: ["A", "B"],
            sections: ["10", "11"],
        });
        document.body.appendChild(nodeListScript);

        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: true,
                status: 200,
                text: () => Promise.resolve(JSON.stringify({ results: [] })),
            })
        );
    });

    afterEach(() => {
        vi.clearAllMocks();
        if (nodeListScript && nodeListScript.parentNode) {
            nodeListScript.parentNode.removeChild(nodeListScript);
        }
        window.history.replaceState({}, "", "/");
    });

    it("sends only title.part citation for internal docs in the /full/ reader view", async () => {
        window.history.replaceState({}, "", "/42/431/full/");

        shallowMount(InternalDocsContainer, {
            props: {
                apiUrl: "/v3/",
                homeUrl: "/",
                title: "42",
                part: "431",
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls).toContain("/v3/resources/internal?citations=42.431");
    });

    it("sends section citation when a section hash is present in the /full/ reader view", async () => {
        window.history.replaceState({}, "", "/42/431/full/#431-10");

        shallowMount(InternalDocsContainer, {
            props: {
                apiUrl: "/v3/",
                homeUrl: "/",
                title: "42",
                part: "431",
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls).toContain("/v3/resources/internal?citations=42.431.10");
    });

    it("sends subpart and section citations for internal docs in a subpart reader view", async () => {
        window.history.replaceState({}, "", "/42/431/Subpart-A/");

        shallowMount(InternalDocsContainer, {
            props: {
                apiUrl: "/v3/",
                homeUrl: "/",
                title: "42",
                part: "431",
            },
        });

        await flushPromises();

        const fetchedUrls = global.fetch.mock.calls.map(([url]) => url);

        expect(fetchedUrls).toContain(
            "/v3/resources/internal?citations=42.431.A&citations=42.431.10&citations=42.431.11"
        );
    });
});
