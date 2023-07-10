import flushPromises from "flush-promises";
import { render, screen } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import { ssaSchema } from "../schemas/tableSchemas";

import HeaderCell from "./HeaderCell.vue";

describe("Statute Table Header Cell", () => {
    describe("SSA table header", () => {
        ssaSchema.forEach((column, index) => {
            it(`Creates a snapshot of header cell for column ${index + 1}`, async () => {
                const wrapper = render(HeaderCell, {
                    props: {
                        cellData: column.header,
                        displayType: "table",
                    },
                });
                await flushPromises();
                expect(wrapper).toMatchSnapshot();
            });
        });
    });
});
