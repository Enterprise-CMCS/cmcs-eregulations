import { render, screen, fireEvent } from "@testing-library/vue";
import JumpTo from "vite/components/JumpTo.vue";
import { describe, it, expect } from "vitest";

import flushPromises from "flush-promises";

describe("Jump to", () => {
    it("Gets a list of parts after title is selected", async () => {
        const wrapper = render(JumpTo, {
            props: {
                apiUrl: "http://localhost:8000/"
            }
        });
        await flushPromises();
        const titles = ["", 42, 45];

        const titleDropdown = await wrapper.findByLabelText(
            "Regulation title number"
        );
        let partDropdown = await screen.findByLabelText(
            "Regulation part number"
        );
        expect(partDropdown._vOptions).toStrictEqual([""]);
        expect(titleDropdown._vOptions).toStrictEqual(titles);
        fireEvent.change(titleDropdown, { target: { value: 42 } });

        await flushPromises();
        let parts = ["", "400", "430", "431", "432", "433"];
        partDropdown = await screen.findByLabelText("Regulation part number");
        expect(partDropdown._vOptions).toStrictEqual(parts);
        parts = ["", "95", "155"];
        fireEvent.change(titleDropdown, { target: { value: 45 } });
        await flushPromises();
        expect(partDropdown._vOptions).toStrictEqual(parts);
        fireEvent.change(partDropdown, { target: { value: "" } });
    });
    it("Checks to see if the snap shot matches", async () => {
        const wrapper = render(JumpTo, {
            props: {
                apiUrl: "http://localhost:8000/"
            }
        });
        expect(wrapper).toMatchSnapshot();
    });
});
