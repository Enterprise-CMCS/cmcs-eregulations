import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import Label from "./Label.vue";

describe("Document Type/Category Label", () => {
    it("Renders a Category Label", async () => {
        const wrapper = render(Label, {
            props: {
                name: "Category Name",
                type: "category",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a Subcategory Label", async () => {
        const wrapper = render(Label, {
            props: {
                name: "Subcategory Name",
                type: "subcategory",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
