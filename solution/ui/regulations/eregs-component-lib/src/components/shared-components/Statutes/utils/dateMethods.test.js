import { describe, it, expect } from "vitest";

import { getDateLabel } from "./dateMethods";

describe("Date Methods", () => {
    describe("getDateLabel", () => {
        it("returns empty string when date is null", () => {
            const label = getDateLabel({ type: "effective", date: null });
            expect(label).toEqual("");
        });

        it("returns empty string when date is undefined", () => {
            const label = getDateLabel({ type: "effective", date: undefined });
            expect(label).toEqual("");
        });

        it("returns empty string when date is empty string", () => {
            const label = getDateLabel({ type: "effective", date: "" });
            expect(label).toEqual("");
        });

        it("returns empty string when type is null", () => {
            const label = getDateLabel({ type: null, date: "2023-08" });
            expect(label).toEqual("");
        });

        it("returns empty string when type is undefined", () => {
            const label = getDateLabel({ type: undefined, date: "2023-08" });
            expect(label).toEqual("");
        });

        it("returns empty string when type is empty string", () => {
            const label = getDateLabel({ type: "", date: "2023-08" });
            expect(label).toEqual("");
        });

        it("returns empty string when date is invalid", () => {
            const label = getDateLabel({ type: "effective", date: "20.22-08" });
            expect(label).toEqual("");
        });

        it("returns properly formatted date string when date and type are valid", () => {
            const label = getDateLabel({ type: "effective", date: "2023-08" });
            expect(label).toEqual("effective Aug 2023");
        });
    });
});
