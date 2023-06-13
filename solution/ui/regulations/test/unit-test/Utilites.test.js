import { getCurrentPageResultsRange } from "utilities/utils.js";

import { describe, it, expect } from "vitest";

describe("Utilities.js", () => {
    it("Gets the current page results range", async () => {
        let obj = { count: 100, page: 1, pageSize: 25 };
        let results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([1, 25]);
        obj = { count: 100, page: 2, pageSize: 25 };
        results = getCurrentPageResultsRange(obj);
        expect(results).toStrictEqual([26, 50]);
    });
});
