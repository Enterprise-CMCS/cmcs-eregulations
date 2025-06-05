import { describe, it, expect } from "vitest";

import RelatedSectionsCollapse from "./RelatedSectionsCollapse.vue";

describe("getCollapseName", () => {
    const doc1 = {
        node_id: "doc1-node_id",
        id: "doc1-id",
    };

    it("returns the id if id exists", async () => {
        expect(RelatedSectionsCollapse.getCollapseName(doc1)).toBe(
            "related citations collapsible doc1-id"
        );
    });

    const doc2 = {
        node_id: "doc2-node_id",
    };

    it("returns the node_id if no id", async () => {
        expect(RelatedSectionsCollapse.getCollapseName(doc2)).toBe(
            "related citations collapsible doc2-node_id"
        );
    });
});
