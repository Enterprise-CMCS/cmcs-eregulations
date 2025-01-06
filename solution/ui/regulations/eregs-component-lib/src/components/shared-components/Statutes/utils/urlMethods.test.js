import { describe, it, expect } from "vitest";

import statutesFixture from "cypress/fixtures/statutes.json";

import {
    houseGovUrl,
    usCodeUrl,
    statuteCompilationUrl,
    ssaGovUrl,
} from "./urlMethods";

describe("Statute Table URL methods", () => {
    describe("houseGovUrl", () => {
        it("returns expected URL string", async () => {
            const statuteItem = statutesFixture[0];
            const computedUrl = houseGovUrl(statuteItem);
            expect(computedUrl).toEqual(
                "https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title42-section1301"
            );
        });
    });

    describe("statuteCompilationUrl", () => {
        it("returns null if source_url is undefined", async () => {
            const undefinedSourceUrl = { source_url: undefined };
            const computedUndefinedUrl =
                statuteCompilationUrl(undefinedSourceUrl);
            expect(computedUndefinedUrl).toBeNull();
        });

        it("returns expected URL string if source_url is valid", async () => {
            const statuteItem = statutesFixture[0];
            const computedUrl = statuteCompilationUrl(statuteItem);
            expect(computedUrl).toEqual(
                "https://www.govinfo.gov/content/pkg/COMPS-8763/pdf/COMPS-8763.pdf"
            );
        });

        it("returns null if source_url is null", async () => {
            const statuteItem = statutesFixture[1];
            const computedUrl = statuteCompilationUrl(statuteItem);
            expect(computedUrl).toBeNull();
        });
    });

    describe("ssaGovUrl", () => {
        it("returns expected URL string", async () => {
            const statuteItem = statutesFixture[0];
            const computedUrl = ssaGovUrl(statuteItem);
            expect(computedUrl).toEqual(
                "https://www.ssa.gov/OP_Home/ssact/title11/1101.htm"
            );
        });

        it("uses 16b for Title 16 URLs", async () => {
            const section1601 = {
                section: "1601",
                title: 42,
                usc: "1381",
                act: "Social Security Act",
                name: "Purpose; appropriations.",
                statute_title: 16,
                statute_title_roman: "XVI",
                source_url:
                    "https://www.govinfo.gov/content/pkg/COMPS-8766/uslm/COMPS-8766.xml",
            };
            const computedUrl = ssaGovUrl(section1601);
            expect(computedUrl).toEqual(
                "https://www.ssa.gov/OP_Home/ssact/title16b/1601.htm"
            );
        });
    });

    describe("usCodeUrl", () => {
        it("returns expected URL string", async () => {
            const statuteItem = statutesFixture[0];
            const computedUrl = usCodeUrl(statuteItem);
            expect(computedUrl).toEqual(
                "https://www.govinfo.gov/link/uscode/42/1301"
            );
        });
    });
});
