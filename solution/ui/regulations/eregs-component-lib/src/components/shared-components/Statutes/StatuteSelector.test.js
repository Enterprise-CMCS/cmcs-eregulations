import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import actsFixture from "cypress/fixtures/acts.json";

import { ACT_TYPES } from "sharedComponents/Statutes/utils/enums.js";
import { shapeTitlesResponse } from "utilities/utils";

import StatuteSelector from "./StatuteSelector.vue";

const SHAPED_TITLES = shapeTitlesResponse({
    actsResults: actsFixture,
    actTypes: ACT_TYPES,
});

describe("Statute Table Selector", () => {
    describe("SSA table type", () => {
        it(`Creates a snapshot of the Statute Selector with default props`, async () => {
            const wrapper = render(StatuteSelector, {
                props: {
                    titles: SHAPED_TITLES,
                },
                stubs: { RouterLink: true },
            });

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
                stubs: { RouterLink: true },
                props: {
                    loading: true,
                    titles: SHAPED_TITLES,
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
                stubs: { RouterLink: true },
                props: {
                    selectedAct: "ssa",
                    selectedTitle: "21",
                    titles: SHAPED_TITLES,
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
