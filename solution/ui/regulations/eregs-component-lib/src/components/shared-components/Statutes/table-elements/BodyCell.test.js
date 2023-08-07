import flushPromises from "flush-promises";
import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import { ssaSchema } from "../schemas/tableSchemas";
import statutesFixture from "cypress/fixtures/statutes.json";

import BodyCell from "./BodyCell.vue";

describe("Statute Table Body Cell", () => {
    describe("SSA table type", () => {
        ssaSchema.forEach((column, index) => {
            it(`Creates a snapshot of a body cell for column ${
                index + 1
            }`, async () => {
                const wrapper = render(BodyCell, {
                    props: {
                        cellData: column,
                        statute: statutesFixture[0],
                    },
                });
                await flushPromises();
                expect(wrapper).toMatchSnapshot();
            });
        });

        it("displays 'None' in Statute Compilation BodyCell when source_url is null", async () => {
            const statuteCompilationCellSchema = ssaSchema[2];

            const wrapper = render(BodyCell, {
                props: {
                    cellData: statuteCompilationCellSchema,
                    statute: statutesFixture[1],
                },
            });
            await flushPromises();

            const nullCell = wrapper.getByTestId("1302-none").textContent;
            expect(nullCell).toEqual("None");

            expect(wrapper).toMatchSnapshot();
        });
    });
});
