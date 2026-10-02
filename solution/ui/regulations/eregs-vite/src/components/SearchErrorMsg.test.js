import flushPromises from "flush-promises";
import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";

import SearchErrorMsg from "./SearchErrorMsg.vue";

describe("Search Error Message", () => {
    it("Renders a message with a search query", async () => {
        const wrapper = mount(SearchErrorMsg, {
            props: {
                searchQuery: "Search Query",
                showApology: true,
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = wrapper.get('[data-testid="error__msg"]');

        expect(errorTextEl.text()).toBe(
            "Sorry, we’re unable to display results for Search Query right now. Please try a different query, try again later, or let us know."
        );

        expect(wrapper.html()).toMatchSnapshot();
    });

    it("Renders a message without a search query", async () => {
        const wrapper = mount(SearchErrorMsg, {
            props: {
                searchQuery: "",
                showApology: true,
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = wrapper.get('[data-testid="error__msg"]');

        expect(errorTextEl.text()).toBe(
            "Sorry, we’re unable to display results right now. Please try a different query, try again later, or let us know."
        );

        expect(wrapper.html()).toMatchSnapshot();
    });

    it("Renders a message without an apology", async () => {
        const wrapper = mount(SearchErrorMsg, {
            props: {
                searchQuery: "",
                surveyUrl: "Survey URL",
            },
        });

        await flushPromises();

        const errorTextEl = wrapper.get('[data-testid="error__msg"]');

        expect(errorTextEl.text()).toBe(
            "Please try a different query, try again later, or let us know."
        );

        expect(wrapper.html()).toMatchSnapshot();
    });
});
