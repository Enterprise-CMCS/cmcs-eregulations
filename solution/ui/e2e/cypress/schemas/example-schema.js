// EXAMPLE SCHEMA

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
