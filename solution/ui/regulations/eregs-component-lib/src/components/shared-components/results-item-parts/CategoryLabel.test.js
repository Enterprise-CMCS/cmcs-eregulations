import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import CategoryLabel from "./CategoryLabel.vue";

describe("Document Type/Category Label", () => {
    it("Renders a Category Label", async () => {
        const wrapper = render(CategoryLabel, {
            props: {
                name: "Category Name",
                type: "category",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });

    it("Renders a Subcategory Label", async () => {
        const wrapper = render(CategoryLabel, {
            props: {
                name: "Subcategory Name",
                type: "subcategory",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
