const itemCategoryDefaultSchema = {
    type: "object",
    properties: {
        id: { type: "number" },
        name: { type: "string" },
        description: { type: "string" },
        show_if_empty: { type: "boolean" },
        is_fr_doc_category: { type: "boolean" },
        type: { type: "string" },
    },
};

const itemCategorySchema = {
    type: "object",
    properties: {
        parent: itemCategoryDefaultSchema,
        ...itemCategoryDefaultSchema.properties,
    },
};

const itemLocationSchema = {
    type: "object",
    properties: {
        id: { type: "number" },
        title: { type: "number" },
        part: { type: "number" },
        type: { type: "string" },
        section_id: { type: "number" },
        parent: { type: "number", nullable: true },
    },
};

export const searchGovResourcesItemSchema = {
    type: "object",
    properties: {
        id: { type: "number" },
        created_at: { type: "string" },
        updated_at: { type: "string" },
        approved: { type: "boolean" },
        snippet: { type: "string", nullable: true },
        category: itemCategorySchema,
        locations: { type: "array", items: itemLocationSchema },
        type: { type: "string" }, // could be enum for supplemental_content, federal_register_doc, et
        date: { type: "string", nullable: true },
        name: { type: "string", nullable: true },
        description: { type: "string" },
        internalURL: { type: "string" },
        name_headline: { type: "string", nullable: true },
        description_headline: { type: "string", nullable: true },
        // ...more for federal_register_doc etc
    },
};

// might need to use $ref to make have required fields for nested schemas
export const getSearchGovResourcesSchema = {
    $id: "searchGovResourcesSchema",
    type: "object",
    properties: {
        count: { type: "number" },
        next: { type: "string", nullable: true },
        previous: { type: "string", nullable: true },
        results: { type: "array", items: searchGovResourcesItemSchema },
    },

    required: ["count", "next", "previous", "results"],
    additionalProperties: false,
};
