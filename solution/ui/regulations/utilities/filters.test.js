import { describe, it, expect } from "vitest";

import { getSubjectName, getSubjectNameParts } from "./filters";

describe("getSubjectName", () => {
    it("should return the short name if it exists", () => {
        expect(
            getSubjectName({
                short_name: "Federal Regulations",
                abbreviation: "CFR",
                full_name: "Code of Federal Regulations",
            })
        ).toBe("Federal Regulations");
    });
    it("should return the abbreviation if it exists and the short name does not", () => {
        expect(
            getSubjectName({
                short_name: null,
                abbreviation: "CFR",
                full_name: "Code of Federal Regulations",
            })
        ).toBe("CFR");
    });
    it("should return the full name if neither the short name nor the abbreviation exist", () => {
        expect(
            getSubjectName({
                short_name: null,
                abbreviation: null,
                full_name: "Code of Federal Regulations",
            })
        ).toBe("Code of Federal Regulations");
    });
});

describe("getSubjectNameParts", () => {
    it("should return an array of tuples", () => {
        expect(
            getSubjectNameParts({
                short_name: "Federal Regulations",
                abbreviation: null,
                full_name: "Code of Federal Regulations",
            })
        ).toStrictEqual([
            ["Federal Regulations", true],
            ["Code of Federal Regulations", false],
        ]);
        expect(
            getSubjectNameParts({
                short_name: null,
                abbreviation: "CFR",
                full_name: "Code of Federal Regulations",
            })
        ).toStrictEqual([
            ["CFR", true],
            ["Code of Federal Regulations", false],
        ]);
        expect(
            getSubjectNameParts({
                short_name: null,
                abbreviation: null,
                full_name: "Code of Federal Regulations",
            })
        ).toStrictEqual([
            [null, false],
            ["Code of Federal Regulations", true],
        ]);
    });
});
