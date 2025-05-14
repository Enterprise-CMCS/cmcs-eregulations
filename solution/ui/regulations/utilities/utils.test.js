import isEqual from "lodash/isEqual";

import {
    createLastUpdatedDates,
    createOneIndexedArray,
    delay,
    formatDate,
    formatResourceCategories,
    getActAbbr,
    getCurrentPageResultsRange,
    getFieldVal,
    getFileNameSuffix,
    getFileTypeButton,
    getFrDocType,
    getQueryParam,
    getRequestParams,
    getSectionsRecursive,
    getTagContent,
    niceDate,
    PARAM_ENCODE_DICT,
    PARAM_VALIDATION_DICT,
    parseError,
    shapeTitlesResponse,
    stripQuotes,
} from "utilities/utils.js";

import { afterEach, describe, it, expect, vi } from "vitest";

import internalDocsFixture from "cypress/fixtures/42.431.internal.json";
import formattedInternalDocsFixture from "cypress/fixtures/42.431.internal-formatted";
import publicDocsFixture from "cypress/fixtures/42.433.10.public.json";
import formattedPublicDocsFixture from "cypress/fixtures/42.433.10.public-formatted";
import parts42Fixture from "cypress/fixtures/parts-42.json";
import parts45Fixture from "cypress/fixtures/parts-45.json";
import categoriesFixture from "cypress/fixtures/categories.json";
import categoriesInternalFixture from "cypress/fixtures/categories-internal.json";
import subjectGroupsFixture from "cypress/fixtures/42.431.E.toc.parts.json";
import subjectGroupsExpectedSectionsFixture from "cypress/fixtures/42.431.E.sections-list.json";

describe("Utilities.js", () => {
    describe("formatResourceCategories", () => {
        it("formats public resources", async () => {
            const formattedResources = formatResourceCategories({
                resources: publicDocsFixture.results,
                categories: categoriesFixture.results,
            });
            expect(formattedResources[0].name).toBe("Proposed and Final Rules");
            expect(formattedResources[0].name).toEqual(
                formattedPublicDocsFixture[0].name
            );
            expect(formattedResources[0].description).toBe(
                "Federal Register documents with agency policy proposals and decisions"
            );
            expect(formattedResources[0].description).toEqual(
                formattedPublicDocsFixture[0].description
            );
            expect(formattedResources[0].supplemental_content[0].title).toBe(
                "Medicaid Program; Increased Federal Medical Assistance Percentage Changes Under the Affordable Care Act of 2010; Correction"
            );
            expect(formattedResources[0].supplemental_content[0].title).toEqual(
                formattedPublicDocsFixture[0].supplemental_content[0].title
            );
        });

        it("formats internal docs", async () => {
            const formattedInternalResources = formatResourceCategories({
                resources: internalDocsFixture.results,
                categories: categoriesInternalFixture.results,
            });

            expect(
                formattedInternalResources[0].supplemental_content[0].file_name
            ).toEqual("ff-test-em-8.pdf");
            expect(
                formattedInternalResources[0].supplemental_content[0].file_name
            ).toEqual(
                formattedInternalDocsFixture[0].supplemental_content[0]
                    .file_name
            );
            expect(
                isEqual(
                    formattedInternalResources[0].supplemental_content[0]
                        .locations,
                    formattedInternalDocsFixture[0].supplemental_content[0]
                        .locations
                )
            ).toBe(true);
            expect(
                isEqual(
                    formattedInternalResources[0].supplemental_content[0]
                        .category,
                    formattedInternalDocsFixture[0].supplemental_content[0]
                        .category
                )
            ).toBe(true);
        });
    });

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

    describe("PARAM_VALIDATION_DICT", () => {
        it("subjects are properly validated as number", async () => {
            expect(PARAM_VALIDATION_DICT.subjects(1)).toBe(true);
            expect(PARAM_VALIDATION_DICT.subjects("1")).toBe(true);
            expect(PARAM_VALIDATION_DICT.subjects("one")).toBe(false);
        });

        it("q is properly validated as string", async () => {
            expect(PARAM_VALIDATION_DICT.q("test")).toBe(true);
            expect(PARAM_VALIDATION_DICT.q(undefined)).toBe(true);
            expect(PARAM_VALIDATION_DICT.q("")).toBe(false);
            expect(PARAM_VALIDATION_DICT.q(1)).toBe(false);
        });

        it("type is properly validated as number", async () => {
            expect(PARAM_VALIDATION_DICT.type("all")).toBe(true);
            expect(PARAM_VALIDATION_DICT.type("internal")).toBe(true);
            expect(PARAM_VALIDATION_DICT.type("regulations")).toBe(true);
            expect(PARAM_VALIDATION_DICT.type("external")).toBe(true);
            expect(
                PARAM_VALIDATION_DICT.type("regulations,external,internal")
            ).toBe(true);
            expect(PARAM_VALIDATION_DICT.type("public")).toBe(false);
            expect(PARAM_VALIDATION_DICT.type("")).toBe(false);
            expect(PARAM_VALIDATION_DICT.type(1)).toBe(false);
        });

        it("page is properly validated as number", async () => {
            expect(PARAM_VALIDATION_DICT.page(1)).toBe(true);
            expect(PARAM_VALIDATION_DICT.page("1")).toBe(true);
            expect(PARAM_VALIDATION_DICT.page("one")).toBe(false);
        });

        it("categories is properly validated as number", async () => {
            expect(PARAM_VALIDATION_DICT.categories(1)).toBe(true);
            expect(PARAM_VALIDATION_DICT.categories("1")).toBe(true);
            expect(PARAM_VALIDATION_DICT.categories("one")).toBe(false);
        });

        it("intcategories is properly validated as number", async () => {
            expect(PARAM_VALIDATION_DICT.intcategories(1)).toBe(true);
            expect(PARAM_VALIDATION_DICT.intcategories("1")).toBe(true);
            expect(PARAM_VALIDATION_DICT.intcategories("one")).toBe(false);
        });
    });

    it("PARAM_ENCODE_DICT.q properly encodes special characters", async () => {
        expect(PARAM_ENCODE_DICT.q(" ")).toBe("%20");
        expect(PARAM_ENCODE_DICT.q("&")).toBe("%26");
        expect(PARAM_ENCODE_DICT.q("%")).toBe("%25");
        expect(PARAM_ENCODE_DICT.q("?")).toBe("%3F");
        expect(PARAM_ENCODE_DICT.q("=")).toBe("%3D");
        expect(PARAM_ENCODE_DICT.q("/")).toBe("%2F");
        expect(PARAM_ENCODE_DICT.q("\\")).toBe("%5C");
        expect(PARAM_ENCODE_DICT.q("#")).toBe("%23");
        expect(PARAM_ENCODE_DICT.q(";")).toBe("%3B");
        expect(PARAM_ENCODE_DICT.q(":")).toBe("%3A");
        expect(PARAM_ENCODE_DICT.q('"')).toBe("%22");
        expect(PARAM_ENCODE_DICT.q("<")).toBe("%3C");
        expect(PARAM_ENCODE_DICT.q(">")).toBe("%3E");
        expect(PARAM_ENCODE_DICT.q("{")).toBe("%7B");
        expect(PARAM_ENCODE_DICT.q("}")).toBe("%7D");
        expect(PARAM_ENCODE_DICT.q("[")).toBe("%5B");
        expect(PARAM_ENCODE_DICT.q("]")).toBe("%5D");
        expect(PARAM_ENCODE_DICT.q("|")).toBe("%7C");
        expect(PARAM_ENCODE_DICT.q("^")).toBe("%5E");
        expect(PARAM_ENCODE_DICT.q("`")).toBe("%60");
        expect(PARAM_ENCODE_DICT.q("@")).toBe("%40");
        expect(PARAM_ENCODE_DICT.q("$")).toBe("%24");
        expect(PARAM_ENCODE_DICT.q("+")).toBe("%2B");
        expect(PARAM_ENCODE_DICT.q(",")).toBe("%2C");
        expect(PARAM_ENCODE_DICT.q("SMDL #12-002")).toBe("SMDL%20%2312-002");
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

        expect(getRequestParams({ queryParams: query1 })).toBe(
            "subjects=1&subjects=2&subjects=3&q=test"
        );

        const query2 = {
            subjects: ["1", "2", "asdf"],
            q: "test",
        };

        expect(getRequestParams({ queryParams: query2 })).toBe(
            "subjects=1&subjects=2&q=test"
        );

        const query3 = {
            subjects: ["1,2", "3"],
            q: "test",
        };

        expect(getRequestParams({ queryParams: query3 })).toBe(
            "subjects=3&q=test"
        );

        const query4 = {
            subjects: "erq",
        };

        expect(getRequestParams({ queryParams: query4 })).toBe("");

        const query5 = {
            q: "",
        };

        expect(getRequestParams({ queryParams: query5 })).toBe("");

        const query6 = {
            subjects: "adasdf",
            q: "",
        };

        expect(getRequestParams({ queryParams: query6 })).toBe("");

        const query7 = {
            subjects: ["1", "2", "3"],
            q: "",
        };

        expect(getRequestParams({ queryParams: query7 })).toBe(
            "subjects=1&subjects=2&subjects=3"
        );

        const query8 = {
            q: "test",
            page: 1,
        };

        expect(getRequestParams({ queryParams: query8 })).toBe("q=test&page=1");

        const query9 = {
            q: "test",
            type: "public",
        };

        expect(getRequestParams({ queryParams: query9 })).toBe("q=test");

        const query10 = {
            q: "test",
            type: "internal",
        };

        expect(getRequestParams({ queryParams: query10 })).toBe(
            "q=test&show_regulations=false&show_public=false"
        );

        const query11 = {
            q: "test",
            type: "regulations",
        };

        expect(getRequestParams({ queryParams: query11 })).toBe(
            "q=test&show_public=false&show_internal=false"
        );

        const query12 = {
            q: "test",
            type: "regulations,internal",
        };

        expect(getRequestParams({ queryParams: query12 })).toBe(
            "q=test&show_public=false"
        );

        const query13 = {
            q: "test",
            type: "regulations,external",
        };

        expect(getRequestParams({ queryParams: query13 })).toBe(
            "q=test&show_internal=false"
        );

        const queryAll = {
            q: "test",
            type: "all",
        };

        expect(getRequestParams({ queryParams: queryAll })).toBe("q=test");

        const queryDisallow1 = {
            q: "test",
            type: "all",
        };

        expect(
            getRequestParams({
                queryParams: queryDisallow1,
                disallowList: ["regulations"],
            })
        ).toBe("q=test&show_regulations=false");

        const queryDisallow2 = {
            q: "test",
            type: "internal,external",
        };

        expect(
            getRequestParams({
                queryParams: queryDisallow2,
                disallowList: ["internal"],
            })
        ).toBe("q=test&show_regulations=false&show_internal=false");

        const queryDisallow3 = {
            q: "test",
        };

        expect(
            getRequestParams({
                queryParams: queryDisallow3,
                disallowList: ["internal"],
            })
        ).toBe("q=test&show_internal=false");

        const queryDisallow4 = {};

        expect(
            getRequestParams({
                queryParams: queryDisallow4,
                disallowList: ["internal"],
            })
        ).toBe("show_internal=false");
    });

    it("gets the proper suffix for a filename or returns null", async () => {
        expect(getFileNameSuffix(null)).toBe(null);
        expect(getFileNameSuffix(undefined)).toBe(null);
        expect(getFileNameSuffix(1)).toBe(null);
        expect(getFileNameSuffix("test")).toBe(null);
        expect(getFileNameSuffix("test.docx.")).toBe(null);
        expect(getFileNameSuffix("test.pdf")).toBe("PDF");
        expect(getFileNameSuffix("https://www.test.pdf")).toBe("PDF");
        expect(getFileNameSuffix("test.pdf#param=val")).toBe("PDF");
        expect(getFileNameSuffix("test.msg")).toBe("Outlook");
        expect(getFileNameSuffix("test.msg/")).toBe("Outlook");
        expect(getFileNameSuffix("test.docx")).toBe("DOCX");
        expect(getFileNameSuffix("test.docx/")).toBe("DOCX");
        expect(getFileNameSuffix("test.docxmsg")).toBe(null);
        expect(getFileNameSuffix("test.docx.msg")).toBe("Outlook");
        expect(getFileNameSuffix("test.docx.msg.txt")).toBe("TXT");
        expect(getFileNameSuffix("testdocxmsgjlkltxt")).toBe(null);
        expect(getFileNameSuffix("www.test.gov")).toBe(null);
        expect(getFileNameSuffix("www.test.com/")).toBe(null);

    });

    describe("getFileTypeButton", () => {
        it("is a DOCX file", async () => {
            expect(
                getFileTypeButton({ fileName: "index_zero.docx", uid: "url" })
            ).toBe(
                "<span data-testid='download-chip-url' class='result__link--file-type'>DOCX</span>"
            );
        });

        it("is a PDF file", async () => {
            expect(
                getFileTypeButton({ fileName: "index_four.pdf", uid: "url" })
            ).toBe("<span data-testid='download-chip-url' class='result__link--file-type'>PDF</span>");
        });

        it("is a MSG file", async () => {
            expect(
                getFileTypeButton({ fileName: "index_five.msg", uid: "url" })
            ).toBe(
                "<span data-testid='download-chip-url' class='result__link--file-type'>Outlook</span>"
            );
        });
    });

    describe("getFrDocType", () => {
        it("returns the correct document type", async () => {
            const doc1 = {
                action_type: "Final",
                correction: true,
                withdrawal: true,
            };
            expect(getFrDocType(doc1)).toBe("WD");

            const doc2 = {
                action_type: "Final",
                correction: true,
                withdrawal: false,
            };
            expect(getFrDocType(doc2)).toBe("CORR");

            const doc3 = {
                action_type: "Final",
                correction: false,
                withdrawal: false,
            };
            expect(getFrDocType(doc3)).toBe("Final");
        });
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

    it("getSectionsRecursive properly gets the sections from a list of subject groups", async () => {
        const sections = getSectionsRecursive(subjectGroupsFixture);
        expect(sections).toStrictEqual(subjectGroupsExpectedSectionsFixture);
    });

    describe("niceDate", () => {
        it('should return "N/A" for null or undefined input', () => {
            expect(niceDate(null)).toBe("N/A");
            expect(niceDate(undefined)).toBe("N/A");
        });

        it('should return "N/A" for an empty string input', () => {
            expect(niceDate("")).toBe("N/A");
        });

        it("should correctly format a valid date", () => {
            expect(niceDate("2023-10-26")).toBe("Oct 26, 2023");
        });

        it("should handle edge cases for the start and end of the month", () => {
            expect(niceDate("2024-01-01")).toBe("Jan 1, 2024");
            expect(niceDate("2024-01-31")).toBe("Jan 31, 2024");
            expect(niceDate("2024-02-01")).toBe("Feb 1, 2024");
            expect(niceDate("2024-02-29")).toBe("Feb 29, 2024");
            expect(niceDate("2024-03-01")).toBe("Mar 1, 2024");
        });

        it("should handle different years correctly", () => {
            expect(niceDate("2022-12-25")).toBe("Dec 25, 2022");
            expect(niceDate("2025-05-15")).toBe("May 15, 2025");
        });

        it("should handle dates in different time zones correctly, even though it always sets the time zone", () => {
            expect(niceDate("2023-10-26")).toBe("Oct 26, 2023");
        });

        it("should handle single digit days", () => {
            expect(niceDate("2024-01-05")).toBe("Jan 5, 2024");
        });
    });

    describe("parseError", () => {
        it("should return an error object with a message from err.message when err.errors is not present", () => {
            const err = { message: "Something went wrong!" };
            const parsedError = parseError(err);
            expect(parsedError).toBeInstanceOf(Error);
            expect(parsedError.message).toBe("Something went wrong!");
            expect(parsedError.code).toBeUndefined();
            expect(parsedError.requestId).toBeUndefined();
            expect(parsedError.status).toBeUndefined();
            expect(parsedError.root).toBeUndefined();
        });

        it("should return an error object with a message from err.errors[...][0] when err.errors is present", () => {
            const err = {
                errors: {
                    someCode: ["Error message from errors object"],
                },
                status: 400,
                requestId: "req-123",
            };
            const parsedError = parseError(err);
            expect(parsedError).toBeInstanceOf(Error);
            expect(parsedError.message).toBe(
                "Error message from errors object"
            );
            expect(parsedError.code).toBe("someCode");
            expect(parsedError.requestId).toBe("req-123");
            expect(parsedError.status).toBe(400);
            expect(parsedError.root).toEqual(err);
        });

        it("should return an error object with a message when err.errors has multiple keys", () => {
            const err = {
                errors: {
                    someCode: ["First message"],
                    secondCode: ["Second Message"],
                },
                status: 500,
                requestId: "req-456",
            };
            const parsedError = parseError(err);
            expect(parsedError).toBeInstanceOf(Error);
            expect(parsedError.message).toBe("First message");
            expect(parsedError.code).toBe("someCode");
            expect(parsedError.requestId).toBe("req-456");
            expect(parsedError.status).toBe(500);
            expect(parsedError.root).toEqual(err);
        });

        it("should return the original error object if it has a detail property even when an error.errors is missing", () => {
            const err = {
                message: "This is a message",
                detail: "More error details here.",
                status: 404,
                requestId: "req-789",
            };
            const parsedError = parseError(err);
            expect(parsedError).toEqual(err);
            expect(parsedError.message).toBe("This is a message");
            expect(parsedError.detail).toBe("More error details here.");
            expect(parsedError.status).toBe(404);
            expect(parsedError.requestId).toBe("req-789");
        });
        it("should handle errors with missing status or requestId", () => {
            const err = {
                errors: {
                    someCode: ["Error message"],
                },
            };
            const parsedError = parseError(err);
            expect(parsedError).toBeInstanceOf(Error);
            expect(parsedError.code).toBe("someCode");
            expect(parsedError.message).toBe("Error message");
            expect(parsedError.requestId).toBeUndefined();
            expect(parsedError.status).toBeUndefined();
            expect(parsedError.root).toEqual(err);

            const err2 = {
                errors: {
                    otherCode: ["Another message"],
                },
                status: 400,
            };
            const parsedError2 = parseError(err2);
            expect(parsedError2).toBeInstanceOf(Error);
            expect(parsedError2.code).toBe("otherCode");
            expect(parsedError2.requestId).toBeUndefined();
            expect(parsedError2.status).toBe(400);
            expect(parsedError2.message).toBe("Another message");
            expect(parsedError2.root).toEqual(err2);
        });

        it("should log the error to the console", () => {
            const err = { message: "Test error" };
            const consoleLogSpy = vi.spyOn(console, "info");
            parseError(err);
            expect(consoleLogSpy).toHaveBeenCalledWith(err);
            consoleLogSpy.mockRestore();
        });
    });

    describe("delay", () => {
        afterEach(() => {
            vi.restoreAllMocks();
        });

        it("should resolve after the specified number of seconds", async () => {
            const seconds = 0.1; // Use a small value for faster testing
            const start = Date.now();
            await delay(seconds);
            const end = Date.now();
            const actualDelay = end - start;
            expect(actualDelay).toBeGreaterThanOrEqual(seconds * 1000 - 200); // Allow some leeway
            expect(actualDelay).toBeLessThan(seconds * 1000 + 200); // Allow some leeway
        });

        it("should call _delay with the correct parameters", async () => {
            const seconds = 2;
            const delaySpy = vi.spyOn(global, "setTimeout");
            await delay(seconds);
            expect(delaySpy).toHaveBeenCalledTimes(1);
            expect(delaySpy).toHaveBeenCalledWith(
                expect.any(Function),
                seconds * 1000
            );
        });

        it("should work correctly with 0 seconds", async () => {
            const seconds = 0;
            const start = Date.now();
            await delay(seconds);
            const end = Date.now();
            const actualDelay = end - start;

            expect(actualDelay).toBeLessThan(100);
        });
    });

    describe("getQueryParam", () => {
        it("should get the expected query parameter", () => {
            const url =
                "https://www.test.com/45/155/Subpart-P/2024-11-01/?highlight=test,testing#155-1515";
            expect(getQueryParam(url, "highlight")).toBe("test,testing");
        });

        it("should return null if the query parameter is not found", () => {
            const url = "http://example.com?test=1&test2=2";
            expect(getQueryParam(url, "test3")).toBe(null);
        });

        it("should return null if the URL does not contain a query string", () => {
            const url = "http://example.com";
            expect(getQueryParam(url, "test")).toBe(null);
        });

        it("should handle query parameters with no values", () => {
            const url = "http://example.com?test";
            expect(getQueryParam(url, "test")).toBe("");
        });

        it("should handle query parameters with no values and other parameters", () => {
            const url = "http://example.com?test&test2=2";
            expect(getQueryParam(url, "test")).toBe("");
            expect(getQueryParam(url, "test2")).toBe("2");
        });
    });

    describe("createOneIndexedArray", () => {
        it("should create an array with the correct length and values", () => {
            const length = 5;
            const arr = createOneIndexedArray(length);
            expect(arr.length).toBe(length);
            expect(arr[0]).toBe(1);
            expect(arr[1]).toBe(2);
            expect(arr[2]).toBe(3);
            expect(arr[3]).toBe(4);
            expect(arr[4]).toBe(5);
        });

        it("should handle a length of 0", () => {
            const length = 0;
            const arr = createOneIndexedArray(length);
            expect(arr.length).toBe(0);
        });

        it("should handle a negative length", () => {
            const length = -3;
            const arr = createOneIndexedArray(length);
            expect(arr.length).toBe(0);
        });
    });

    describe("stripQuotes", () => {
        it("should remove quotes from the beginning and end of a string", () => {
            expect(stripQuotes('"test"')).toBe("test");
            expect(stripQuotes("'test'")).toBe("test");
            expect(stripQuotes('"test')).toBe("test");
            expect(stripQuotes("test")).toBe("test");
        });

        it("should handle empty strings", () => {
            expect(stripQuotes("")).toBe("");
        });

        it("should handle strings with only quotes", () => {
            expect(stripQuotes('"')).toBe("");
            expect(stripQuotes("'")).toBe("");
        });
    });

    describe("getTagContent", () => {
        it("should return the content of a single tag with matching class", () => {
            const tagClass = "correct__class";
            const html =
                "<div class='container__class'><span class='ignored__class'>not target content</span><span class='correct__class'>target content</span></div>";
            expect(getTagContent(html, tagClass)).toStrictEqual([
                "target content",
            ]);
        });

        it("should return the content of multiple tags with matching class", () => {
            const tagClass = "correct__class";
            const html =
                "<div class='container__class'><span class='ignored__class'>not target content</span><span class='correct__class'>target content</span></div><span class='correct__class'>more target content</span>";
            expect(getTagContent(html, tagClass)).toStrictEqual([
                "target content",
                "more target content",
            ]);
        });
    });

    describe("formatDate", () => {
        it("should correctly format a valid date string", () => {
            expect(formatDate("2023-10-26T12:00:00Z")).toBe("Oct 26, 2023");
            expect(formatDate("2024-01-01T00:00:00Z")).toBe("Jan 1, 2024");
            expect(formatDate("2024-12-31T23:59:59Z")).toBe("Dec 31, 2024");
        });

        it("should correctly format four-letter month names", () => {
            expect(formatDate("2023-07-15T12:00:00Z")).toBe("July 15, 2023");
            expect(formatDate("2024-03-10T00:00:00Z")).toBe("Mar 10, 2024");
        });

        it("should correctly format a date object", () => {
            expect(formatDate(new Date("2023-07-15T12:00:00Z"))).toBe(
                "July 15, 2023"
            );
            expect(formatDate(new Date("2024-03-10T00:00:00Z"))).toBe(
                "Mar 10, 2024"
            );
        });

        it('should handle invalid date inputs by returning "Invalid Date"', () => {
            const actualResult1 = formatDate("hello");
            const expectedResult1 = "Invalid Date";

            expect(actualResult1).toEqual(expectedResult1);
        });

        it("should handle dates at the beginning and end of the year correctly", () => {
            expect(formatDate("2023-01-01T00:00:00Z")).toBe("Jan 1, 2023");
            expect(formatDate("2023-12-31T23:59:59Z")).toBe("Dec 31, 2023");
        });

        it("should handle single digit days", () => {
            expect(formatDate("2024-01-05T12:00:00Z")).toBe("Jan 5, 2024");
            expect(formatDate("2024-02-08T00:00:00Z")).toBe("Feb 8, 2024");
        });

        it("should handle leap year correctly", () => {
            expect(formatDate("2024-02-29T10:00:00Z")).toBe("Feb 29, 2024");
        });

        it("should handle null or undefined inputs", () => {
            expect(formatDate(null)).toEqual("Invalid Date");
            expect(formatDate(undefined)).toEqual("Invalid Date");
        });

        it("should handle empty string inputs", () => {
            expect(formatDate("")).toEqual("Invalid Date");
        });
    });

    describe("getFieldVal", () => {
        it("should return the value from item.resource if item.resource exists", () => {
            const item = {
                name: "Jonathan Doe",
                resource: { name: "John Doe" },
                reg_text: { name: "Jane Doe" },
            };
            expect(getFieldVal({ item, fieldName: "name" })).toBe("John Doe");
        });

        it("should return the value from item.reg_text if item.resource does not exist but item.reg_text exists", () => {
            const item = {
                city: "Baltimore",
                reg_text: { city: "New York" },
            };
            expect(getFieldVal({ item, fieldName: "city" })).toBe("New York");
        });

        it("should return the value from item if item.resource and item.reg_text do not exist", () => {
            const item = { id: 123 };
            expect(getFieldVal({ item, fieldName: "id" })).toBe(123);
        });

        it("should return undefined if item.resource exists but fieldName does not exist on item.resource", () => {
            const item = { resource: { name: "John Doe" } };
            expect(getFieldVal({ item, fieldName: "age" })).toBeUndefined();
        });

        it("should return undefined if item.reg_text exists but fieldName does not exist on item.reg_text", () => {
            const item = { reg_text: { city: "New York" } };
            expect(getFieldVal({ item, fieldName: "country" })).toBeUndefined();
        });

        it("should return undefined if item does not have the fieldName", () => {
            const item = { id: 123 };
            expect(getFieldVal({ item, fieldName: "name" })).toBeUndefined();
        });

        it("should return undefined if item is null", () => {
            expect(
                getFieldVal({ item: null, fieldName: "name" })
            ).toBeUndefined();
        });

        it("should return undefined if item is undefined", () => {
            expect(
                getFieldVal({ item: undefined, fieldName: "name" })
            ).toBeUndefined();
        });

        it("should return undefined if item is an empty object", () => {
            expect(
                getFieldVal({ item: {}, fieldName: "name" })
            ).toBeUndefined();
        });

        it("should return 0 if the field value is explicitly 0", () => {
            const item = { id: 0 };
            expect(getFieldVal({ item, fieldName: "id" })).toBe(0);
        });

        it("should return a nested object if the field value is a nested object", () => {
            const nestedObject = { address: "test street" };
            const item = { resource: { nestedObject: nestedObject } };

            expect(getFieldVal({ item, fieldName: "nestedObject" })).toEqual(
                nestedObject
            );
        });
    });
});
