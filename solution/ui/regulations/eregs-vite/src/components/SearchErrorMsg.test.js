import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import SearchErrorMsg from "./SearchErrorMsg.vue";

describe("Search Error Message", () => {
    it("Renders a message with a search query", async () => {
        const wrapper = render(SearchErrorMsg, {
            props: {
                searchQuery: "Search Query",
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = screen.getByText((content, element) =>
            content.startsWith("Sorry")
        );

        expect(errorTextEl.textContent).toBe(
            "Sorry, we’re unable to display results for Search Query right now. please try a different query, try again later, or let us know."
        );

        const letterToCapitalize = screen.getByTestId(
            "error-msg__common--first-letter"
        );

        expect(
            letterToCapitalize.classList.contains(
                "error-msg__common--first-letter"
            )
        ).toBe(true);

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a message without a search query", async () => {
        const wrapper = render(SearchErrorMsg, {
            props: {
                searchQuery: "",
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = screen.getByText((content, element) =>
            content.startsWith("Sorry")
        );

        expect(errorTextEl.textContent).toBe(
            "Sorry, please try a different query, try again later, or let us know."
        );

        const letterToCapitalize = screen.getByTestId(
            "error-msg__common--first-letter"
        );

        expect(
            letterToCapitalize.classList.contains(
                "error-msg__common--first-letter"
            )
        ).toBe(false);


        expect(wrapper).toMatchSnapshot();
    });
});
