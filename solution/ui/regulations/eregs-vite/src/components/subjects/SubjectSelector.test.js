import { describe, it, expect } from "vitest";

import SubjectSelector from "./SubjectSelector.vue";

describe("Subject Selector", () => {
    it("gets the correct input container classes", () => {
        expect(
            SubjectSelector.getInputContainerClasses({ parent: "search" })
        ).toStrictEqual({
            "subjects__input--sidebar": false,
        });

        expect(
            SubjectSelector.getInputContainerClasses({ parent: "subjects" })
        ).toStrictEqual({
            "subjects__input--sidebar": true,
        });
    });

    it("gets the correct list item classes", () => {
        expect(
            SubjectSelector.getListItemClasses({ parent: "search" })
        ).toStrictEqual({
            sidebar__li: false,
        });

        expect(
            SubjectSelector.getListItemClasses({ parent: "subjects" })
        ).toStrictEqual({
            sidebar__li: true,
        });
    });

    it("gets the correct subject classes", () => {
        expect(
            SubjectSelector.getSubjectClasses({
                subjectId: 20,
                subjectQueryParam: "10",
            })
        ).toStrictEqual({
            "subjects-li__button": true,
            "subjects-li__button--selected": false,
        });

        expect(
            SubjectSelector.getSubjectClasses({
                subjectId: 20,
                subjectQueryParam: "20",
            })
        ).toStrictEqual({
            "subjects-li__button": true,
            "subjects-li__button--selected": true,
        });
    });

    it("gets the correct filter reset classes", () => {
        expect(
            SubjectSelector.getFilterResetClasses({ filter: "query string" })
        ).toStrictEqual({
            "subjects__filter-reset": true,
            "subjects__filter-reset--hidden": false,
        });

        expect(
            SubjectSelector.getFilterResetClasses({ filter: "" })
        ).toStrictEqual({
            "subjects__filter-reset": true,
            "subjects__filter-reset--hidden": true,
        });
    });

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
