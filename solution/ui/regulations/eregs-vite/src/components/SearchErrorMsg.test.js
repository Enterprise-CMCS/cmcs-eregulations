import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import SearchErrorMsg from "./SearchErrorMsg.vue";

describe("Search Error Message", () => {
    it("Renders a message with a search query", async () => {
        const wrapper = render(SearchErrorMsg, {
            props: {
                searchQuery: "Search Query",
                showApology: true,
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = screen.getByTestId("error__msg");

        expect(errorTextEl.textContent).toBe(
            "Sorry, we’re unable to display results for Search Query right now. Please try a different query, try again later, or let us know."
        );

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a message without a search query", async () => {
        const wrapper = render(SearchErrorMsg, {
            props: {
                searchQuery: "",
                showApology: true,
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = screen.getByTestId("error__msg");

        expect(errorTextEl.textContent).toBe(
            "Sorry, we’re unable to display results right now. Please try a different query, try again later, or let us know."
        );

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a message without an apology", async () => {
        const wrapper = render(SearchErrorMsg, {
            props: {
                searchQuery: "",
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = screen.getByTestId("error__msg");

        expect(errorTextEl.textContent).toBe(
            "Please try a different query, try again later, or let us know."
        );

        expect(wrapper).toMatchSnapshot();
    });
});
