import { describe, it, expect } from "vitest";

import SelectedSubjectChip from "./SelectedSubjectChip.vue";

describe("SelectedSubjectChip", () => {
    it("returns the correct display count", () => {
        const subject1 = {
            count: 1,
        };
        expect(SelectedSubjectChip.getCount(subject1)).toBe(1);
        expect(SelectedSubjectChip.getDisplayCount(subject1)).toBe(
            '<span class="count">(1)</span>'
        );

        const subject2 = {};
        expect(SelectedSubjectChip.getDisplayCount(subject2)).toBe("");

        const subject3 = {
            public_resources: 1,
        };
        expect(SelectedSubjectChip.getCount(subject3)).toBe(1);
        expect(SelectedSubjectChip.getDisplayCount(subject3)).toBe(
            '<span class="count">(1)</span>'
        );

        const subject4 = {
            public_resources: 1,
            internal_resources: 1,
        };
        expect(SelectedSubjectChip.getCount(subject4)).toBe(2);
        expect(SelectedSubjectChip.getDisplayCount(subject4)).toBe(
            '<span class="count">(2)</span>'
        );
    });
});
