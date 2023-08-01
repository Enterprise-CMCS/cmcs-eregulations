import {
    getActAbbr,
    getCurrentPageResultsRange,
    romanize,
    shapeTitlesResponse,
} from "utilities/utils.js";

import { describe, it, expect } from "vitest";

describe("Utilities.js", () => {
    it("getCurrentPageResultsRange properly gets the current page results range", async () => {
        let obj = { count: 100, page: 1, pageSize: 25 };
        let results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([1, 25]);

        obj = { count: 100, page: 2, pageSize: 25 };
        results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([26, 50]);
    });

    it("romanize properly converts numbers to roman numerals", async () => {
        expect(romanize(1)).toBe("I");
        expect(romanize(2)).toBe("II");
        expect(romanize(21)).toBe("XXI");
        expect(romanize(1936)).toBe("MCMXXXVI");
    });

    it("getActAbbr returns expected act abbreviation", async () => {
        const actsResults = [
            {
                act: "Social Security Act",
                title: 11,
                title_roman: "XI",
            },
        ];
        const actTypes = [
            { aca: "Affordable Care Act" },
            { ssa: "Social Security Act" },
        ];

        expect(getActAbbr({ act: actsResults[0].act, actTypes })).toBe("ssa");
        expect(getActAbbr({ act: actsResults[0].act, actTypes })).not.toBe(
            "aca"
        );
    });

    it("shapeTitlesResponse properly shapes /v3/acts Response to be used in StatuteSelector", async () => {
        const actsResults = [
            {
                act: "Social Security Act",
                title: 11,
                title_roman: "XI",
            },
        ];
        const actTypes = [
            { aca: "Affordable Care Act" },
            { ssa: "Social Security Act" },
        ];
        const shapedTitles = shapeTitlesResponse({
            actsResults,
            actTypes,
        });

        expect(shapedTitles).toStrictEqual({
            ssa: {
                name: "Social Security Act",
                titles: [
                    {
                        title: "11",
                        titleRoman: "XI",
                    },
                ],
            },
        });
    });
});
