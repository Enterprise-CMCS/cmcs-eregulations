import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/vue";

import AccessLink from "./AccessLink.vue";

describe("Access Link", () => {
    it("Renders a link with the correct base path and active class", async () => {
        window.location = { pathname: "/test/base/get-account-access/" };

        render(AccessLink, {
            props: {
                base: "/test/base/",
            },
        });

        const accessLinkEl = screen.getByTestId("get-account-access-narrow");

        expect(accessLinkEl.href).toBe(
            "http://mock-url.com/test/base/get-account-access/"
        );

        expect(accessLinkEl.classList).toContain("active");
    });
});
