import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import policyDocsFixture from "cypress/fixtures/policy-docs.json";

import DivisionLabel from "./DivisionLabel.vue";

describe("DivisionLabel", () => {
    it("Renders a Division Label component", async () => {
        const wrapper = render(DivisionLabel, {
            props: {
                division: policyDocsFixture.results[1].division,
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
