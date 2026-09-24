import { fireEvent, render, screen, waitFor } from "@testing-library/vue";
import { describe, expect, it, vi } from "vitest";

import JumpTo from "./JumpTo.vue";

const { getParts, getTitles } = vi.hoisted(() => ({
    getParts: vi.fn(),
    getTitles: vi.fn(),
}));

vi.mock("utilities/api.js", () => ({
    getParts,
    getTitles,
}));

describe("JumpTo", () => {
    it("keeps parts from the currently selected title when older requests finish later", async () => {
        let resolveInitialParts;
        let resolveSelectedParts;
        getTitles.mockResolvedValue(["42", "45"]);
        getParts.mockImplementation(({ title }) => new Promise((resolve) => {
            if (title === "42") {
                resolveInitialParts = resolve;
            } else {
                resolveSelectedParts = resolve;
            }
        }));

        render(JumpTo, { props: { apiUrl: "/v3/" } });

        await waitFor(() => expect(resolveInitialParts).toBeTypeOf("function"));
        await fireEvent.update(screen.getByLabelText("Regulation title number"), "45");
        await waitFor(() => expect(resolveSelectedParts).toBeTypeOf("function"));

        resolveSelectedParts([{ name: "95" }]);
        await waitFor(() => {
            expect(screen.getByLabelText("Regulation part number").value).toBe("");
            expect(screen.getByLabelText("Regulation part number").querySelector('option[value="95"]')).not.toBeNull();
        });

        resolveInitialParts([{ name: "400" }]);
        await waitFor(() => {
            expect(screen.getByLabelText("Regulation part number").querySelector('option[value="95"]')).not.toBeNull();
            expect(screen.getByLabelText("Regulation part number").querySelector('option[value="400"]')).toBeNull();
        });
    });
});
