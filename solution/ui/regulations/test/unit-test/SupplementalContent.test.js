import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/vue";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import SupplementalContent from "eregsComponentLib/src/components/SupplementalContent.vue";
import flushPromises from "flush-promises";
import { categories, subCategories } from "../../msw/mocks/categories";

describe("Supplemental Content", () => {
    beforeEach(() => {
        const docCat = document.createElement("div");
        docCat.id = "categories";
        docCat.textContent = JSON.stringify(categories);
        const subcat = document.createElement("div");
        subcat.id = "sub_categories";
        subcat.textContent = JSON.stringify(subCategories);
        document.body.appendChild(docCat);
        document.body.appendChild(subcat);

     })
     afterEach(() => {
        const cat = document.getElementById("categories");
        const sub = document.getElementById("sub_categories");
        cat.remove();
        sub.remove();

     })
    it("Populates some content", async () => {
        const wrapper = render(SupplementalContent, {
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
    it("Clicks a drop down", async () => {
        const wrapper = render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"]
            }
        });
        await flushPromises();
        const subG = await screen.getByLabelText("expand Subregulatory Guidance");
        expect(subG).toBeTruthy();
        await fireEvent.click(subG)

        expect(subG.textContent).toStrictEqual('Subregulatory Guidance ');
        const stateMedBtn = await screen.getByText("State Medicaid Director Letter (SMDL)")
        await flushPromises();
        expect(stateMedBtn.classList.contains("visible")).toBe(false)
        await fireEvent.click(stateMedBtn);
        
        expect(stateMedBtn.classList.contains("visible")).toBe(true)
    });

    //  leaving out for now.  test-id is causing issues
    // it("Checks to see if the snap shot matches", async () => {
    //     const wrapper = render(SupplementalContent, {
    //         props: {
    //             apiUrl: "http://localhost:8000/",
    //             title: "42",
    //             part: "433",
    //             subparts: ["A"]
    //         }
    //     });
    //     await flushPromises();
    //     expect(wrapper).toMatchSnapshot();
    // });
});
