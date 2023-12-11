import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import DocTypeLabel from "./DocTypeLabel.vue";

describe("Public/Private label", () => {
    it("Renders a Public Label", async () => {
        const wrapper = render(DocTypeLabel, {
            props: {
                iconType: "users",
                docType: "External",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a Private Label", async () => {
        const wrapper = render(DocTypeLabel, {
            props: {
                iconType: "key",
                docType: "Internal",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
