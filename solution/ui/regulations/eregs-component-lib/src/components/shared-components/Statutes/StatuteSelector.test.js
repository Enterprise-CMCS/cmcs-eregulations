import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import actsFixture from "cypress/fixtures/acts.json";

import { ACT_TYPES } from "sharedComponents/Statutes/utils/enums.js";
import { shapeTitlesResponse } from "utilities/utils";

import StatuteSelector from "./StatuteSelector.vue";

const SHAPED_TITLES = shapeTitlesResponse({
    actsResults: actsFixture,
    actTypes: ACT_TYPES,
});

const vuetify = createVuetify({
    components,
    directives,
});

global.ResizeObserver = require("resize-observer-polyfill");

describe("Statute Table Selector", () => {
    describe("SSA table type", () => {
        it(`Creates a snapshot of the Statute Selector with default props`, async () => {
            const wrapper = render(StatuteSelector, {
                global: {
                    plugins: [vuetify],
                },
                props: {
                    titles: SHAPED_TITLES,
                },
                stubs: { RouterLink: true },
            });

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XIX-19");
            expect(
                activeLink.classList.contains("v-tab-item--selected")
            ).toBe(true);

            const inactiveLink = screen.getByTestId("ssa-XXI-21");
            expect(
                inactiveLink.classList.contains("v-tab-item--selected")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });

        it(`Creates a snapshot of the Statute Selector with a loading prop`, async () => {
            const wrapper = render(StatuteSelector, {
                global: {
                    plugins: [vuetify],
                },
                props: {
                    loading: true,
                    titles: SHAPED_TITLES,
                },
                stubs: { RouterLink: true },
            });

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XIX-19");

            const inactiveLink = screen.getByTestId("ssa-XXI-21");
            expect(
                inactiveLink.classList.contains("v-tab-item--selected")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });

        it(`Creates a snapshot of the Statute Selector when act and title props passed in to component`, async () => {
            const wrapper = render(StatuteSelector, {
                global: {
                    plugins: [vuetify],
                },
                props: {
                    selectedAct: "ssa",
                    selectedTitle: "21",
                    titles: SHAPED_TITLES,
                },
                stubs: { RouterLink: true },
            });

            await flushPromises();

            const activeLink = screen.getByTestId("ssa-XXI-21");
            expect(
                activeLink.classList.contains("v-tab-item--selected")
            ).toBe(true);

            const inactiveLink = screen.getByTestId("ssa-XIX-19");
            expect(
                inactiveLink.classList.contains("titles-list__link--active")
            ).toBe(false);

            expect(wrapper).toMatchSnapshot();
        });
    });
});
