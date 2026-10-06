import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";

import IconCard from "./IconCard.vue";

describe("IconCard", () => {
    describe("renders the correct icon based on the icon prop", () => {
        it("renders the 'book' icon when iconType is 'book'", () => {
            const wrapper = mount(IconCard, {
                props: {
                    iconType: "book",
                },
            });

            expect(wrapper.find('[data-testid="icon--book"]').exists()).toBe(true);
            expect(wrapper.html()).toMatchSnapshot();
        });

        it("renders the 'book' icon when iconType is 'book'", () => {
            const wrapper = mount(IconCard, {
                props: {
                    iconType: "clipboard",
                },
            });

            expect(wrapper.find('[data-testid="icon--clipboard"]').exists()).toBe(true);
            expect(wrapper.html()).toMatchSnapshot();
        });

        it("renders the 'book' icon when iconType is 'book'", () => {
            const wrapper = mount(IconCard, {
                props: {
                    iconType: "search",
                },
            });

            expect(wrapper.find('[data-testid="icon--search"]').exists()).toBe(true);
            expect(wrapper.html()).toMatchSnapshot();
        });
    });
});
