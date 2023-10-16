import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import SubjectChip from "./SubjectChip.vue";

describe("Subject Chip", () => {
    it("Renders a Subject Chip", async () => {
        const wrapper = render(SubjectChip, {
            props: {
                subjectName: "Subject Name",
            },
        });

        expect(wrapper).toMatchSnapshot();
    });
});
