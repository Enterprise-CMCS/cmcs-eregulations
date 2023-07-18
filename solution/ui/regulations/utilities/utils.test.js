import { getCurrentPageResultsRange, romanize } from "utilities/utils.js";

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

    it("Romanizes numbers", async () => {
        expect(romanize(1)).toBe("I");
        expect(romanize(2)).toBe("II");
        expect(romanize(21)).toBe("XXI");
        expect(romanize(1936)).toBe("MCMXXXVI");
    });
});
