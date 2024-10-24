import { describe, it, expect } from "vitest";

import SubjectSelector from "./SubjectSelector.vue";

describe("Subject Selector", () => {
    it("returns the correct display count", () => {
        const subject1 = {
            count: 1,
        };
        expect(SubjectSelector.getDisplayCount(subject1)).toBe(
            '<span class="count">(1)</span>'
        );
        const subject2 = {};
        expect(SubjectSelector.getDisplayCount(subject2)).toBe("");
    });
});
