import { render, screen } from "@testing-library/vue";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import LastParserSuccessDate from "eregsComponentLib/src/components/LastParserSuccessDate.vue";

describe("LastParserSuccessDate", () => {
    beforeEach(() => {});
    afterEach(() => {});
    it("Populates some content", async () => {
        render(LastParserSuccessDate, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
            },
        });
        setTimeout(() => {
            const successDate = screen.getByText("Jun 28, 2023");
            expect(successDate).toBeTruthy();
        }, 1000);
    });
    it("Creates a snapshot of parserdate", async () => {
        const wrapper = render(LastParserSuccessDate, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
            },
        });
        setTimeout(() => {
            expect(wrapper).toMatchSnapshot();
        }, 1000);
    });
});
