// SSA
const houseGovUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title${title}-section${usc}`;
};

const usCodeUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://www.govinfo.gov/link/uscode/${title}/${usc}`;
};

const statuteCompilationUrl = (statuteObj) => {
    const { source_url } = statuteObj;
    const compsNumber = source_url
        .split("/")
        .find((str) => str.includes("COMPS"));
    return `https://www.govinfo.gov/content/pkg/${compsNumber}/pdf/${compsNumber}.pdf`;
};

const ssaGovUrl = (statuteObj) => {
    const { statute_title, section } = statuteObj;
    return `https://www.ssa.gov/OP_Home/ssact/title${statute_title}/${section}.htm`;
};

export { houseGovUrl, usCodeUrl, statuteCompilationUrl, ssaGovUrl };
