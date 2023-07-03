// SSA
/**
 * @param {Object} statuteObj - object containing statute information
 * @param {number} statuteObj.title - CFR title (ex: 42)
 * @param {string} statuteObj.usc - USC section
 *
 * @returns {string} url - url to the House.gov page for the USC section
 */
const houseGovUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title${title}-section${usc}`;
};

/**
 * @param {Object} statuteObj - object containing statute information
 * @param {string} statuteObj.souce_url - URL containing COMPS number
 *
 * @returns {string} url - url to GovInfo.gov page displaying Statute Compilation PDF
 */
const statuteCompilationUrl = (statuteObj) => {
    const { source_url } = statuteObj;
    const compsNumber = source_url
        .split("/")
        .find((str) => str.includes("COMPS"));
    return `https://www.govinfo.gov/content/pkg/${compsNumber}/pdf/${compsNumber}.pdf`;
};

/**
 * @param {Object} statuteObj - object containing statute information
 * @param {number} statuteObj.statute_title - integer representation of roman numeral Statute Title
 * @param {string} statuteObj.section - SSA section
 *
 * @returns {string} url - url to the SSA.gov page for the SSA section
 */
const ssaGovUrl = (statuteObj) => {
    const { statute_title, section } = statuteObj;
    return `https://www.ssa.gov/OP_Home/ssact/title${statute_title}/${section}.htm`;
};

/**
 * @param {Object} statuteObj - object containing statute information
 * @param {number} statuteObj.title - CFR title (ex: 42)
 * @param {string} statuteObj.usc - USC section
 *
 * @returns {string} url - url to GovInfo.gov PDF page for USC Code
 */
const usCodeUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://www.govinfo.gov/link/uscode/${title}/${usc}`;
};

export { houseGovUrl, usCodeUrl, statuteCompilationUrl, ssaGovUrl };
