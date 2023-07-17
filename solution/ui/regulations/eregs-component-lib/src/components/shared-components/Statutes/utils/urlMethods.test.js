import {
    houseGovUrl,
    usCodeUrl,
    statuteCompilationUrl,
    ssaGovUrl,
} from "./urlMethods";

import statutesFixture from "cypress/fixtures/statutes.json";

import { describe, it, expect } from "vitest";

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
        it("returns expected URL string", async () => {
            const statuteItem = statutesFixture[0];
            const computedUrl = statuteCompilationUrl(statuteItem);
            expect(computedUrl).toEqual(
                "https://www.govinfo.gov/content/pkg/COMPS-8763/pdf/COMPS-8763.pdf"
            );
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
