// SSA table URL methods

/**
 * @param {number} title - CFR title (ex: 42)
 * @param {string} usc - USC section
 *
 * @returns {string} url - url to the House.gov page for the USC section
 */
const houseGovUrl = ({ title, usc } = {}) => {
    const prefix = "https://uscode.house.gov/";

    if (!title && !usc) return prefix;

    return `${prefix}view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title${title}-section${usc}`;
}

/**
 * @param {string} souce_url - URL containing COMPS number
 *
 * @returns {string | null} url - url to GovInfo.gov page displaying Statute Compilation PDF
 */
const statuteCompilationUrl = ({ source_url, blank=false } = {}) => {
    if (blank) return "https://www.govinfo.gov/app/collection/comps/";
    if (!source_url) return null;

    const compsNumber = source_url
        .split("/")
        .find((str) => str.includes("COMPS"));

    return `https://www.govinfo.gov/content/pkg/${compsNumber}/pdf/${compsNumber}.pdf`;
};

/**
 * @param {number} statute_title - integer representation of roman numeral Statute Title
 * @param {string} section - SSA section
 *
 * @returns {string} url - url to the SSA.gov page for the SSA section
 */
const ssaGovUrl = ({ statute_title, section } = {}) => {
    const prefix = "https://www.ssa.gov/OP_Home/ssact/";

    if (!statute_title && !section) return `${prefix}ssact.htm`;

    const title = statute_title == "16" ? "16b" : statute_title;

    return `https://www.ssa.gov/OP_Home/ssact/title${title}/${section}.htm`;
};

/**
 * @param {number} title - CFR title (ex: 42)
 * @param {string} usc - USC section
 *
 * @returns {string} url - url to GovInfo.gov PDF page for USC Code
 */
const usCodeUrl = ({ title, usc } = {}) => {
    if (!title && !usc) return "https://www.govinfo.gov/app/collection/uscode";

    return `https://www.govinfo.gov/link/uscode/${title}/${usc}`;
}

export { houseGovUrl, usCodeUrl, statuteCompilationUrl, ssaGovUrl };
