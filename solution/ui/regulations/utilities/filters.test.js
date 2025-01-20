import { describe, it, expect } from "vitest";

import {
    formatDate,
    getSubjectName,
    getSubjectNameParts,
    locationLabel,
    locationUrl,
    sortSubjects,
} from "./filters";

describe("filters", () => {
    describe("formatDate", () => {
        it("should format a valid date string with month and day", () => {
            expect(formatDate("2023-10-26")).toBe("October 26, 2023");
            expect(formatDate("2024-01-01")).toBe("January 1, 2024");
            expect(formatDate("2024-12-31")).toBe("December 31, 2024");
        });

        it("should format a valid date string with only month and year", () => {
            expect(formatDate("2024-01")).toBe("January 2024");
            expect(formatDate("2024-12")).toBe("December 2024");
        });

        it("should format a valid date string with only a year", () => {
            expect(formatDate("2023")).toBe("2023");
            expect(formatDate("2024")).toBe("2024");
        });

        it("should handle different valid date formats", () => {
            expect(formatDate("2023-10-05")).toBe("October 5, 2023");
            expect(formatDate("2023-11-25")).toBe("November 25, 2023");
        });

        it('should handle invalid date strings and return "Invalid Date"', () => {
            expect(formatDate("invalid-date")).toBe("Invalid Date");
            expect(formatDate("2023/10/26")).toBe("2023/10/26");
            expect(formatDate("2023-10")).toBe("October 2023");
        });

        it("should handle leap year dates", () => {
            expect(formatDate("2024-02-29")).toBe("February 29, 2024");
        });

        it("should handle dates at the beginning and end of the year", () => {
            expect(formatDate("2023-01-01")).toBe("January 1, 2023");
            expect(formatDate("2023-12-31")).toBe("December 31, 2023");
        });

        it("should handle single digit days", () => {
            expect(formatDate("2024-01-05")).toBe("January 5, 2024");
            expect(formatDate("2024-02-08")).toBe("February 8, 2024");
        });

        it('should handle null or undefined inputs by returning "Invalid Date"', () => {
            expect(formatDate(null)).toBe("Invalid Date");
            expect(formatDate(undefined)).toBe("Invalid Date");
        });

        it('should handle empty string input by returning "Invalid Date"', () => {
            expect(formatDate("")).toBe("Invalid Date");
        });

        it("should handle year values that are strings", () => {
            expect(formatDate("2023")).toBe("2023");
        });

        it("should not crash if a non-string is provided", () => {
            expect(formatDate(123)).toBe("Invalid Date");
            expect(formatDate(["2023-10-26"])).toBe("Invalid Date");
            expect(formatDate({ date: "2023-10-26" })).toBe("Invalid Date");
        });
    });

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

    describe("sortSubjects", () => {
        it("should sort subjects by name", () => {
            const subjects = [
                {
                    short_name: "Federal Regulations",
                    abbreviation: null,
                    full_name: "Code of Federal Regulations",
                },
                {
                    short_name: null,
                    abbreviation: "CFR",
                    full_name: "Code of Federal Regulations",
                },
                {
                    short_name: null,
                    abbreviation: null,
                    full_name: "Code of Federal Regulations",
                },
            ];

            expect(subjects.sort(sortSubjects)).toStrictEqual([
                {
                    short_name: null,
                    abbreviation: "CFR",
                    full_name: "Code of Federal Regulations",
                },
                {
                    short_name: null,
                    abbreviation: null,
                    full_name: "Code of Federal Regulations",
                },
                {
                    short_name: "Federal Regulations",
                    abbreviation: null,
                    full_name: "Code of Federal Regulations",
                },
            ]);
        });
    });

    describe("locationLabel", () => {
        it("should return a formatted section label", () => {
            const location = { type: "Section", part: "100", section_id: "12" };
            expect(locationLabel(location)).toBe("100.12");
        });

        it("should return a formatted section label with different part and section id", () => {
            const location = { type: "Section", part: "200", section_id: "1" };
            expect(locationLabel(location)).toBe("200.1");
        });

        it("should return a formatted subpart label", () => {
            const location = { type: "Subpart", part: "100", subpart_id: "A" };
            expect(locationLabel(location)).toBe("100 Subpart A");
        });

        it("should return a formatted subpart label with different part and subpart id", () => {
            const location = { type: "Subpart", part: "200", subpart_id: "B" };
            expect(locationLabel(location)).toBe("200 Subpart B");
        });

        it("should handle type in mixed case correctly", () => {
            const location1 = {
                type: "sEcTiOn",
                part: "100",
                section_id: "12",
            };
            expect(locationLabel(location1)).toBe("100.12");
            const location2 = { type: "sUbPaRt", part: "100", subpart_id: "A" };
            expect(locationLabel(location2)).toBe("100 Subpart A");
        });

        it("should handle special characters in subpart ids", () => {
            const location = {
                type: "Subpart",
                part: "100",
                subpart_id: "A-1",
            };
            expect(locationLabel(location)).toBe("100 Subpart A-1");
        });

        it("should handle missing section_id for section", () => {
            const location = { type: "Section", part: "100" };
            expect(locationLabel(location)).toBe("100.undefined");
        });

        it("should handle missing subpart_id for subpart", () => {
            const location = { type: "Subpart", part: "100" };
            expect(locationLabel(location)).toBe("100 Subpart undefined");
        });

        it("should handle missing type, part, section_id, subpart_id", () => {
            const location = {};
            expect(locationLabel(location)).toBe("Invalid Location");
        });
    });

    describe("locationUrl", () => {
        it("should return a formatted URL for a subpart", () => {
            const location = {
                title: "42",
                type: "Subpart",
                part: "100",
                subpart_id: "A",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/42/100/Subpart-A/"
            );
        });

        it("should return a formatted URL for a subpart with different title, part, and subpart", () => {
            const location = {
                title: "50",
                type: "Subpart",
                part: "200",
                subpart_id: "B",
            };
            const base = "https://test.com/";
            expect(locationUrl(location, base)).toBe(
                "https://test.com/50/200/Subpart-B/"
            );
        });

        it("should return a formatted URL for a section", () => {
            const location = {
                title: "42",
                type: "Section",
                part: "100",
                section_id: "12",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/42/100/12#100-12"
            );
        });

        it("should return a formatted URL for a section with different title, part, and section", () => {
            const location = {
                title: "50",
                type: "Section",
                part: "200",
                section_id: "1",
            };
            const base = "https://test.com/";
            expect(locationUrl(location, base)).toBe(
                "https://test.com/50/200/1#200-1"
            );
        });

        it("should handle type in mixed case correctly", () => {
            const location1 = {
                title: "42",
                type: "sUbPaRt",
                part: "100",
                subpart_id: "A",
            };
            const base1 = "https://example.com/";
            expect(locationUrl(location1, base1)).toBe(
                "https://example.com/42/100/Subpart-A/"
            );

            const location2 = {
                title: "42",
                type: "sEcTiOn",
                part: "100",
                section_id: "12",
            };
            const base2 = "https://example.com/";
            expect(locationUrl(location2, base2)).toBe(
                "https://example.com/42/100/12#100-12"
            );
        });

        it("should handle special characters in subpart_id", () => {
            const location = {
                title: "42",
                type: "Subpart",
                part: "100",
                subpart_id: "A-1",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/42/100/Subpart-A-1/"
            );
        });

        it("should handle missing section_id for a section", () => {
            const location = {
                title: "42",
                type: "Section",
                part: "100",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/42/100/undefined#100-undefined"
            );
        });

        it("should handle missing subpart_id for a subpart", () => {
            const location = {
                title: "42",
                type: "Subpart",
                part: "100",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/42/100/Subpart-undefined/"
            );
        });

        it("should handle missing title, part, section_id, subpart_id", () => {
            const location = {
                type: "Section",
            };
            const base = "https://example.com/";
            expect(locationUrl(location, base)).toBe(
                "https://example.com/undefined/undefined/undefined#undefined-undefined"
            );
            const location2 = {
                type: "Subpart",
            };
            const base2 = "https://example.com/";
            expect(locationUrl(location2, base2)).toBe(
                "https://example.com/undefined/undefined/Subpart-undefined/"
            );
        });
    });
});
