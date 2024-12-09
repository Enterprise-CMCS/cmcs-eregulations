import { describe, it, expect } from "vitest";

import IndicatorLabel from "./IndicatorLabel.vue";

describe("Indicator Label", () => {
    it("gets the correct indicator classes", () => {
        const prop1 = {
            type: "WD",
        };

        expect(IndicatorLabel.getIndicatorClasses(prop1)).toEqual({
            "secondary-indicator": false,
            "tertiary-indicator": true,
        });

        const prop2 = {
            type: "Final",
        };

        expect(IndicatorLabel.getIndicatorClasses(prop2)).toEqual(undefined);

        const prop3 = {
            type: "CORR",
        };

        expect(IndicatorLabel.getIndicatorClasses(prop3)).toEqual({
            "secondary-indicator": true,
            "tertiary-indicator": false,
        });
    });
});
