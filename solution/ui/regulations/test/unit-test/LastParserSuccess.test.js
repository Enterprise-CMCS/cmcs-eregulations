import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import LastParserSuccessDate from "eregsComponentLib/src/components/LastParserSuccessDate.vue";
import flushPromises from "flush-promises";

describe("LastParserSuccessDate", () => {
    beforeEach(() => {});
    afterEach(() => {});
    it("Renders N/A as expected", async () => {
        const wrapper = mount(LastParserSuccessDate, {
            props: {
                apiUrl: "test/n/a/",
            },
        });
        await flushPromises();
        expect(wrapper.text()).toContain("N/A");
    });
    it("Populates some content", async () => {
        const wrapper = mount(LastParserSuccessDate, {
            props: {
                apiUrl: "test/success/",
            },
        });
        await flushPromises();
        expect(wrapper.text()).toContain("Jun 28, 2023");
    });
    it("Creates a snapshot of parserdate", async () => {
        const wrapper = mount(LastParserSuccessDate, {
            props: {
                apiUrl: "test/snapshot/",
            },
        });
        expect(wrapper.html()).toMatchSnapshot();
    });
});
