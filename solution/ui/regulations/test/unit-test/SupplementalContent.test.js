import { render, screen, fireEvent, waitFor } from "@testing-library/vue";
import { describe, it, expect, beforeEach } from "vitest";
import SupplementalContent from "eregsComponentLib/src/components/SupplementalContent.vue";
import flushPromises from "flush-promises";
import { categories, subCategories } from "../../msw/mocks/categories";

describe("Supplemental Content", () => {
    beforeEach(() => {


     })
    it("Populates some content", async () => {
        const docCat = document.createElement("div");
        docCat.id = "categories";
        docCat.textContent = JSON.stringify(categories);
        const subcat = document.createElement("div");
        subcat.id = "sub_categories";
        subcat.textContent = JSON.stringify(subCategories);
        document.body.appendChild(docCat);
        document.body.appendChild(subcat);

        render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"]
            }
        });
        await flushPromises();

        const view = screen.getByText("Subpart A Resources");
        expect(view.id).toBe("subpart-resources-heading");
        const subG = screen.getByText("Subregulatory Guidance");
        expect(subG).toBeTruthy();
    });

    it("Checks to see if the snap shot matches", async () => {
        const docCat = document.createElement("div");
        docCat.id = "categories";
        docCat.textContent = JSON.stringify(categories);
        const subcat = document.createElement("div");
        subcat.id = "sub_categories";
        subcat.textContent = JSON.stringify(subCategories);
        document.body.appendChild(docCat);
        document.body.appendChild(subcat);
        const wrapper = render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"]
            }
        });
        await flushPromises();
        expect(wrapper).toMatchSnapshot();
    });
});
