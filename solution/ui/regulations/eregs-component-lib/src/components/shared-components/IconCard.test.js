import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/vue";

import IconCard from "./IconCard.vue";

describe("IconCard", () => {
    describe("renders the correct icon based on the icon prop", () => {
        it("renders the 'book' icon when iconType is 'book'", () => {
            const bookWrapper = render(IconCard, {
                props: {
                    iconType: "book",
                },
            });

            screen.getByTestId("icon--book");
            expect(bookWrapper).toMatchSnapshot();
        });

        it("renders the 'book' icon when iconType is 'book'", () => {
            const bookWrapper = render(IconCard, {
                props: {
                    iconType: "clipboard",
                },
            });

            screen.getByTestId("icon--clipboard");
            expect(bookWrapper).toMatchSnapshot();
        });

        it("renders the 'book' icon when iconType is 'book'", () => {
            const bookWrapper = render(IconCard, {
                props: {
                    iconType: "search",
                },
            });

            screen.getByTestId("icon--search");
            expect(bookWrapper).toMatchSnapshot();
        });
    });

});
