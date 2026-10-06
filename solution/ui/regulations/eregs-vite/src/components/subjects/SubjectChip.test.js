import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";

import SubjectChip from "./SubjectChip.vue";

describe("Subject Chip", () => {
    it("Renders a Subject Chip", async () => {
        const wrapper = mount(SubjectChip, {
            props: {
                subjectName: "Subject Name",
                subjectId: 2,
            },
        });

        expect(wrapper.html()).toMatchSnapshot();
    });
});
