import {
    createLastUpdatedDates,
    getActAbbr,
    getCurrentPageResultsRange,
    getRequestParams,
    romanize,
    shapeTitlesResponse,
} from "utilities/utils.js";

import { describe, it, expect } from "vitest";

import parts42Fixture from "cypress/fixtures/parts-42.json";
import parts45Fixture from "cypress/fixtures/parts-45.json";

describe("Utilities.js", () => {
    it("createLastUpdatedDates properly creates last updated dates", async () => {
        const partsArrays = [parts42Fixture, parts45Fixture];
        const lastUpdatedDates = createLastUpdatedDates(partsArrays);

        expect(lastUpdatedDates).toStrictEqual({
            95: "2019-11-05",
            155: "2023-06-18",
            400: "2023-01-01",
            430: "2017-01-20",
            431: "2023-01-01",
            432: "2020-06-30",
            433: "2023-08-31",
            434: "2017-01-01",
            435: "2023-01-01",
            436: "2017-01-01",
            438: "2021-07-01",
            440: "2020-12-16",
            441: "2023-08-04",
            442: "2017-01-01",
            447: "2023-01-01",
            455: "2023-01-01",
            456: "2021-03-01",
            457: "2023-08-31",
            460: "2023-08-04",
        });
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

    it("getCurrentPageResultsRange properly gets the current page results range", async () => {
        let obj = { count: 100, page: 1, pageSize: 25 };
        let results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([1, 25]);

        obj = { count: 100, page: 2, pageSize: 25 };
        results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([26, 50]);
    });

    it("getRequestParams properly gets the request params to be used for an API call", async () => {
        const query1 = {
            subjects: ["1", "2", "3"],
            q: "test",
        };

        expect(getRequestParams(query1)).toBe(
            "subjects=1&subjects=2&subjects=3&q=test"
        );

        const query2 = {
            subjects: ["1", "2", "asdf"],
            q: "test",
        };

        expect(getRequestParams(query2)).toBe("subjects=1&subjects=2&q=test");

        const query3 = {
            subjects: ["1,2", "3"],
            q: "test",
        };

        expect(getRequestParams(query3)).toBe("subjects=3&q=test");

        const query4 = {
            subjects: "erq",
        };

        expect(getRequestParams(query4)).toBe("");

        const query5 = {
            q: "",
        };

        expect(getRequestParams(query5)).toBe("");

        const query6 = {
            subjects: "adasdf",
            q: "",
        };

        expect(getRequestParams(query6)).toBe("");

        const query7 = {
            subjects: ["1", "2", "3"],
            q: "",
        };

        expect(getRequestParams(query7)).toBe(
            "subjects=1&subjects=2&subjects=3"
        );

        const query8 = {
            q: "test",
            page: 1,
        };

        expect(getRequestParams(query8)).toBe("q=test");
    });

    it("romanize properly converts numbers to roman numerals", async () => {
        expect(romanize(1)).toBe("I");
        expect(romanize(2)).toBe("II");
        expect(romanize(21)).toBe("XXI");
        expect(romanize(1936)).toBe("MCMXXXVI");
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
