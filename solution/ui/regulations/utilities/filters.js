/**
 * @param dateString {string} - a date string in YYYY-MM-DD format
 * @returns {string} - a date string in Month D/DD, YYYY format
 */
const formatDate = (dateString) => {
    const date = new Date(dateString);
    let options = { year: "numeric", timeZone: "UTC" };
    const raw_date = dateString.split("-");
    if (raw_date.length > 1) {
        options.month = "long";
    }
    if (raw_date.length > 2) {
        options.day = "numeric";
    }
    const format = new Intl.DateTimeFormat("en-US", options);
    return format.format(date);
};

/**
 * @param identifierAndDescription {string} - a string with a part/subpart identifier and a description of the contents of that part/subpart, separated by a dash or an em dash
 * @returns {string} - a string containing only the description
 */
const getDescriptionOnly = (identifierAndDescription) => {
    const splitIndex = identifierAndDescription.includes("-")
        ? identifierAndDescription.indexOf("-")
        : identifierAndDescription.indexOf("—");

    return identifierAndDescription.substring(splitIndex + 1);
};

/**
 * @param location {Object} - a Subpart or Section of the Regs
 * @param location.title {string} - the title number of the location (ex: 42)
 * @param location.type {string} - the type of location (ex: Subpart, Section)
 * @param location.part {string} - the part number for the location
 * @param location.section_id {?string} - the section number
 * @param location.subpart_id {?string} - the subpart name
 * @returns {string} - a properly formatted label
 */
const locationLabel = ({ type, part, section_id, subpart_id }) => {
    return type.toLowerCase() === "section"
        ? `${part}.${section_id}`
        : `${part} Subpart ${subpart_id}`;
};

/**
 * @param location {Object} - a Subpart or Section of the Regs
 * @param location.title {string} - the title number of the location (ex: 42)
 * @param location.type {string} - the type of location (ex: Subpart, Section)
 * @param location.part {string} - the part number for the location
 * @param location.section_id {?string} - the section number
 * @param location.subpart_id {?string} - the subpart name
 * @param base {string} - base to be prepended to returned URL
 * @returns {string} - URL to location
 */
const locationUrl = ({ title, type, part, section_id, subpart_id }, base) => {
    // early return if related regulation is a subpart and not a section
    if (type.toLowerCase() === "subpart") {
        return `${base}${title}/${part}/Subpart-${subpart_id}/`;
    }

    return `${base}${title}/${part}/${section_id}#${part}-${section_id}`;
};

/**
 * @param subject {Object} - a subject
 * @param subject.short_name {?string} - the short name of the subject
 * @param subject.abbreviation {?string} - the abbreviation of the subject
 * @param subject.full_name {?string} - the full name of the subject
 * @returns {string} - a properly formatted subject name
 * @example
 * getSubjectName({ short_name: "Federal Regulations", abbreviation: "CFR", full_name: "Code of Federal Regulations" }) // "Federal Regulations"
 */
const getSubjectName = (subject) =>
    subject.short_name || subject.abbreviation || subject.full_name;


export {
    formatDate,
    getDescriptionOnly,
    getSubjectName,
    locationLabel,
    locationUrl,
};
