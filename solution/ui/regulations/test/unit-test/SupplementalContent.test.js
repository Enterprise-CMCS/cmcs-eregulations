import { render, screen, fireEvent } from "@testing-library/vue";
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import SupplementalContent from "eregsComponentLib/src/components/SupplementalContent.vue";
import flushPromises from "flush-promises";
import { categories } from "../../msw/mocks/categories";

describe("Supplemental Content", () => {
    beforeEach(() => {
        const docCat = document.createElement("div");
        docCat.id = "categories";
        docCat.textContent = JSON.stringify(categories);
        document.body.appendChild(docCat);

        const url = "http://eregs.com/";

        Object.defineProperty(window, "location", {
            value: new URL(url),
        });
    });

    afterEach(() => {
        const cat = document.getElementById("categories");
        cat.remove();
    });

    it("Populates some content", async () => {
        render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        await flushPromises();

        const view = screen.getByText("Subpart A Resources");
        expect(view.id).toBe("subpart-resources-heading");

        const subG = screen.getByText("Subregulatory Guidance");
        expect(subG).toBeTruthy();
    });

    it("Properly shows and hides empty categories", async () => {
        render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        await flushPromises();

        const subEmptyButVisible = screen.queryByText("Empty but Visible");
        expect(subEmptyButVisible).toBeTruthy();

        const subEmptyAndHidden = screen.queryByText("Empty and Hidden");
        expect(subEmptyAndHidden).toBeNull();
    });

    it("Clicks a drop down", async () => {
        render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        await flushPromises();
        const subG = await screen.getByLabelText(
            "expand Subregulatory Guidance"
        );
        expect(subG).toBeTruthy();

        await fireEvent.click(subG);
        expect(subG.textContent).toStrictEqual("Subregulatory Guidance ");

        const stateMedBtn = await screen.getByText(
            "State Medicaid Director Letter (SMDL)"
        );
        await flushPromises();
        expect(stateMedBtn.classList.contains("visible")).toBe(false);

        await fireEvent.click(stateMedBtn);
        expect(stateMedBtn.classList.contains("visible")).toBe(true);
    });

    it("Navigates to a section then a subpart", async () => {
        window.location.href += "#433-10";

        render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        expect(window.location.hash).toEqual("#433-10");

        await flushPromises();
        const heading = screen.getByText("§ 433.10 Resources");
        expect(heading.id).toBe("subpart-resources-heading");

        let viewAllSubpartRes = screen.getByTestId(
            "view-all-subpart-resources"
        );
        expect(viewAllSubpartRes.textContent).toBe(
            " View All Subpart A Resources (136) "
        );

        const subG = screen.getByLabelText("expand Subregulatory Guidance");
        await fireEvent.click(subG);

        const stateHealth = screen.getByLabelText(
            "expand State Health Official (SHO) Letter"
        );
        await fireEvent.click(stateHealth);
        await fireEvent.click(viewAllSubpartRes);

        await flushPromises();

        viewAllSubpartRes = screen.queryByTestId("view-all-subpart-resources");
        expect(viewAllSubpartRes).toBeFalsy();

        expect(heading.textContent).toBe("Subpart A Resources");

        const relatedStatues = screen.getByLabelText("expand Related Statutes");
        expect(relatedStatues).toBeTruthy();

        await fireEvent.click(relatedStatues);
    });

    it("Checks to see if the snap shot matches", async () => {
        const wrapper = render(SupplementalContent, {
            props: {
                apiUrl: "http://localhost:8000/",
                title: "42",
                part: "433",
                subparts: ["A"],
            },
        });

        await flushPromises();

        expect(wrapper).toMatchSnapshot();
    });
});
