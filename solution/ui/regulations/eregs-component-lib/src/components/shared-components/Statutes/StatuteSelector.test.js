import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import StatuteSelector from "./StatuteSelector.vue";

describe("Statute Table Selector", () => {
    describe("SSA table type", () => {
        it(`Creates a snapshot of the Statute Selector with default props`, async () => {
            const wrapper = render(StatuteSelector);

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XIX-19");
            expect(
                activeLink.classList.contains("titles-list__link--active")
            ).toBe(true);
            expect(
                activeLink.classList.contains("titles-list__link--loading")
            ).toBe(false);

            const inactiveLink = screen.getByTestId("ssa-XXI-21");
            expect(
                inactiveLink.classList.contains("titles-list__link--active")
            ).toBe(false);
            expect(
                inactiveLink.classList.contains("titles-list__link--loading")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });

        it(`Creates a snapshot of the Statute Selector with a loading prop`, async () => {
            const wrapper = render(StatuteSelector, {
                props: {
                    loading: true,
                },
            });

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XIX-19");
            expect(
                activeLink.classList.contains("titles-list__link--loading")
            ).toBe(true);

            const inactiveLink = screen.getByTestId("ssa-XXI-21");
            expect(
                inactiveLink.classList.contains("titles-list__link--active")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });

        it(`Creates a snapshot of the Statute Selector when act and title props passed in to component`, async () => {
            const wrapper = render(StatuteSelector, {
                props: {
                    selectedAct: "ssa",
                    selectedTitle: "21",
                },
            });

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XXI-21");
            expect(
                activeLink.classList.contains("titles-list__link--active")
            ).toBe(true);

            const inactiveLink = screen.getByTestId("ssa-XIX-19");
            expect(
                inactiveLink.classList.contains("titles-list__link--active")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });
    });
});
