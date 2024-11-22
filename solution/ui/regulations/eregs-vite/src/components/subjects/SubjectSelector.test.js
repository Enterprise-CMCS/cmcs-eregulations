import { describe, it, expect } from "vitest";

import SubjectSelector from "./SubjectSelector.vue";

describe("Subject Selector", () => {
    it("removes selected subject from subjects list", () => {
        const subjectsList = [
            {
                id: 20,
                full_name: "Aged, Blind, Disabled",
                short_name: "",
                abbreviation: "ABD",
                description: "",
            },
            {
                id: 24,
                full_name: "Alternative Benefit Plan",
                short_name: "",
                abbreviation: "ABP",
                description: "",
            },
        ];
        const subjectId = "20";
        expect(
            SubjectSelector.getUnselectedSubjects({ subjectsList, subjectId })
        ).toStrictEqual(subjectsList.slice(1));

        const subjectId2 = "24";
        expect(
            SubjectSelector.getUnselectedSubjects({
                subjectsList,
                subjectId: subjectId2,
            })
        ).toStrictEqual(subjectsList.slice(0, 1));

        const subjectId3 = "30";
        expect(
            SubjectSelector.getUnselectedSubjects({
                subjectsList,
                subjectId: subjectId3,
            })
        ).toStrictEqual(subjectsList);
    });
});
