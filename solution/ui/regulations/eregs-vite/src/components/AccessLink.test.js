import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";

import AccessLink from "./AccessLink.vue";

describe("Access Link", () => {
    it("Renders a link with the correct base path and active class", async () => {
        window.location = { pathname: "/test/base/get-account-access/" };

        const wrapper = mount(AccessLink, {
            props: {
                base: "/test/base/",
            },
        });

        const accessLinkEl = wrapper.get('[data-testid="get-account-access-narrow"]');

        expect(accessLinkEl.element.href).toBe(
            "http://mock-url.com/test/base/get-account-access/"
        );

        expect(accessLinkEl.classes()).toContain("active");
    });
});
