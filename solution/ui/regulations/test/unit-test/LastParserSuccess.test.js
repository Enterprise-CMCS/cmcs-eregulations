import { render, screen } from "@testing-library/vue";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import LastParserSuccessDate from "eregsComponentLib/src/components/LastParserSuccessDate.vue";
import flushPromises from "flush-promises";

describe("LastParserSuccessDate", () => {
    beforeEach(() => {});
    afterEach(() => {});
    it("Renders N/A as expected", async () => {
        render(LastParserSuccessDate, {
            props: {
                apiUrl: "test/n/a/",
            },
        });
        await flushPromises();
        const naDate = screen.getByText("N/A");
        expect(naDate).toBeTruthy();
    });
    it("Populates some content", async () => {
        render(LastParserSuccessDate, {
            props: {
                apiUrl: "test/success/",
            },
        });
        await flushPromises();
        const successDate = screen.getByText("Jun 28, 2023");
        expect(successDate).toBeTruthy();
    });
    it("Creates a snapshot of parserdate", async () => {
        const wrapper = render(LastParserSuccessDate, {
            props: {
                apiUrl: "test/snapshot/",
            },
        });
        expect(wrapper).toMatchSnapshot();
    });
});
