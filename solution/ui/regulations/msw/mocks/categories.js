const categories = [
    {
        id: 5,
        name: "Subregulatory Guidance",
        description: "SMDLs, SHOs, CIBs, FAQs, SMM",
        order: 400,
        show_if_empty: true,
        abstractcategory_ptr_id: 5,
    },
    {
        id: 11,
        name: "Implementation Resources",
        description:
            "State Technical Assistance, Toolkits, SPA/Waiver Resources",
        order: 500,
        show_if_empty: true,
        abstractcategory_ptr_id: 11,
    },
    {
        id: 19,
        name: "Reports to Congress",
        description:
            "CMS policy analysis and research reports sent to Congress",
        order: 501,
        show_if_empty: true,
        abstractcategory_ptr_id: 19,
    },
    {
        id: 23,
        name: "Oversight Reports",
        description:
            "Reports from HHS Office of Inspector General and U.S. Government Accountability Office",
        order: 600,
        show_if_empty: true,
        abstractcategory_ptr_id: 23,
    },
];
const subCategories = [{}];
export { categories, subCategories };
