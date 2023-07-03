import { render, screen } from "@testing-library/vue";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import LastParserSuccessDate from "eregsComponentLib/src/components/LastParserSuccessDate.vue";
import flushPromises from "flush-promises";

describe("LastParserSuccessDate", () => {
    beforeEach(() => {});
    afterEach(() => {});
    it("Populates some content", async () => {
        render(LastParserSuccessDate, {
            props: {
                apiUrl: "http://localhost:8000/"
            }
        });
        await flushPromises();
        const successDate = screen.getByText("Jun 28, 2023");
        expect(successDate).toBeTruthy();
    });
    it("Creates a snapshot of parserdate", async () => {
        const wrapper = render(LastParserSuccessDate, {
            props: {
                apiUrl: "http://localhost:8000/"
            }
        });
        await flushPromises();
        expect(wrapper).toMatchSnapshot();
    });
});
