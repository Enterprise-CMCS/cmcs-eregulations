import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import DocTypeLabel from "./DocTypeLabel.vue";

describe("Public/Private label", () => {
    it("Renders a Public Label", async () => {
        const wrapper = render(DocTypeLabel, {
            props: {
                iconType: "external",
                docType: "Public",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a Private Label", async () => {
        const wrapper = render(DocTypeLabel, {
            props: {
                iconType: "internal",
                docType: "Internal",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
