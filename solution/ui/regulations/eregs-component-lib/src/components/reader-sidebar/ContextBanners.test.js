import { describe, it, expect } from "vitest";

import ContextBanners from "./ContextBanners.vue";

describe("Context Banners", () => {
    it("correctly gets section key from hash", () => {
        const hash1 = "#433-123";
        const hash2 = "#433.456";
        const hash3 = "#main-content";
        const hash4 = "";

        expect(ContextBanners.getSectionKeyFromHash({ hash: hash1, part: 42 })).toBe("42.123");
        expect(ContextBanners.getSectionKeyFromHash({ hash: hash2, part: 42 })).toBe("433.456");
        expect(ContextBanners.getSectionKeyFromHash({ hash: hash3, part: 42 })).toBe("");
        expect(ContextBanners.getSectionKeyFromHash({ hash: hash4, part: 42 })).toBe("");
    });
});
