import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";

import CollapseButton from "./CollapseButton.vue";

describe("CollapseButton", () => {
    it("renders with aria-expanded='false' when collapsed and does not override accessible name with aria-label", () => {
        const wrapper = mount(CollapseButton, {
            props: {
                name: "test-collapse",
                state: "collapsed",
            },
            slots: {
                collapsed: "Show Details",
                expanded: "Hide Details",
            },
        });

        const button = wrapper.find("button");
        expect(button.attributes("aria-expanded")).toBe("false");
        expect(button.attributes("aria-label")).toBeUndefined();
        expect(button.text()).toBe("Show Details");
    });

    it("renders with aria-expanded='true' when expanded", () => {
        const wrapper = mount(CollapseButton, {
            props: {
                name: "test-collapse",
                state: "expanded",
            },
            slots: {
                collapsed: "Show Details",
                expanded: "Hide Details",
            },
        });

        const button = wrapper.find("button");
        expect(button.attributes("aria-expanded")).toBe("true");
        expect(button.attributes("aria-label")).toBeUndefined();
        expect(button.text()).toBe("Hide Details");
    });

    it("toggles aria-expanded and slot content when clicked", async () => {
        const wrapper = mount(CollapseButton, {
            props: {
                name: "test-collapse",
                state: "collapsed",
            },
            slots: {
                collapsed: "Show Details",
                expanded: "Hide Details",
            },
        });

        const button = wrapper.find("button");
        expect(button.attributes("aria-expanded")).toBe("false");
        expect(button.text()).toBe("Show Details");

        await button.trigger("click");

        expect(button.attributes("aria-expanded")).toBe("true");
        expect(button.text()).toBe("Hide Details");
    });
});
