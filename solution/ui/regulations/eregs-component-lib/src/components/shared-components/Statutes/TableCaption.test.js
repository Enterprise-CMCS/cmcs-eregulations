import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import TableCaption from "./TableCaption.vue";

describe("Statute Table Caption", () => {
    it(`Creates a snapshot of the Statute Selector with default props`, async () => {
        const wrapper = render(TableCaption);
        expect(wrapper).toMatchSnapshot();
    });
});
