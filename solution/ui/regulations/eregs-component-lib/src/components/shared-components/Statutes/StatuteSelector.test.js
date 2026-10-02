import flushPromises from "flush-promises";
import { mount } from "@vue/test-utils";
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
        it("Creates a snapshot of the Statute Selector with default props", async () => {
            const wrapper = mount(StatuteSelector, {
                global: {
                    plugins: [vuetify],
                    stubs: { RouterLink: true },
                },
                props: {
                    titles: SHAPED_TITLES,
                },
            });

            await flushPromises();

            const activeLink = wrapper.get('[data-testid="ssa-XIX-19"]');
            expect(
                activeLink.classes()
            ).toContain("v-tab-item--selected");

            const inactiveLink = wrapper.get('[data-testid="ssa-XXI-21"]');
            expect(
                inactiveLink.classes()
            ).not.toContain("v-tab-item--selected");

            expect(wrapper.html()).toMatchSnapshot();
        });

        it("Creates a snapshot of the Statute Selector when act and title props passed in to component", async () => {
            const wrapper = mount(StatuteSelector, {
                global: {
                    plugins: [vuetify],
                    stubs: { RouterLink: true },
                },
                props: {
                    selectedAct: "ssa",
                    selectedTitle: "21",
                    titles: SHAPED_TITLES,
                },
            });

            await flushPromises();

            const activeLink = wrapper.get('[data-testid="ssa-XXI-21"]');
            expect(
                activeLink.classes()
            ).toContain("v-tab-item--selected");

            const inactiveLink = wrapper.get('[data-testid="ssa-XIX-19"]');
            expect(
                inactiveLink.classes()
            ).not.toContain("titles-list__link--active");

            expect(wrapper.html()).toMatchSnapshot();
        });
    });
});
