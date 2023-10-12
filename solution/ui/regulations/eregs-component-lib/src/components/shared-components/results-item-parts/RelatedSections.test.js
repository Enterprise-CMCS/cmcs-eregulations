import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import { createLastUpdatedDates } from "utilities/utils.js";

import parts42Fixture from "cypress/fixtures/parts-42.json";
import parts45Fixture from "cypress/fixtures/parts-45.json";
import resourcesFixture from "cypress/fixtures/resources.json";

import RelatedSections from "./RelatedSections.vue";

describe("Related Sections", () => {
    it("Renders a Related Sections component", async () => {
        const wrapper = render(RelatedSections, {
            props: {
                base: "/",
                item: resourcesFixture.results[0],
                partsLastUpdated: createLastUpdatedDates([
                    parts42Fixture,
                    parts45Fixture,
                ]),
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
