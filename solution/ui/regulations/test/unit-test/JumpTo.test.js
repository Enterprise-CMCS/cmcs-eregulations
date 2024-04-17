import { render, screen, fireEvent } from "@testing-library/vue";
import JumpTo from "vite/components/JumpTo.vue";
import { describe, it, expect } from "vitest";

import flushPromises from "flush-promises";

describe("Jump to", () => {
    it("Checks to see if the snap shot matches", async () => {
        const wrapper = render(JumpTo, {
            props: {
                apiUrl: "http://localhost:8000/"
            }
        });
        expect(wrapper).toMatchSnapshot();
    });
});
