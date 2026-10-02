import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import GovInfoLinks from "eregsComponentLib/src/components/GovInfoLinks.vue";
import flushPromises from "flush-promises";

describe("Gov Info Links", () => {
    beforeEach(() => {});
    afterEach(() => {});
    it("Populates checks if years populate", async () => {
        const wrapper = mount(GovInfoLinks, {
            props: {
                apiUrl: "http://localhost:9000/",
                title: "42",
                part: "431",
                section: "10"
            }
        });
        await flushPromises();
        const yearLink = wrapper.findAll("a").find((a) => a.text() === "2022");
        expect(yearLink.attributes("href")).toStrictEqual(
            "https://www.govinfo.gov/content/pkg/CFR-2022-title42-vol4/pdf/CFR-2022-title42-vol4-sec431-10.pdf"
        );
        const missingYear = wrapper.findAll("a").find((a) => a.text() === "189829829");
        expect(missingYear).toBeUndefined();
    });
    it("Creates a snapshot of GovInfo", async () => {
        const wrapper = mount(GovInfoLinks, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "431",
                section: "10"
            }
        });
        await flushPromises();
        expect(wrapper.html()).toMatchSnapshot();
    });
});
