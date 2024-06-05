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
 * @param subject.short_name {string | null} - the short name of the subject
 * @param subject.abbreviation {string | null} - the abbreviation of the subject
 * @param subject.full_name {string} - the full name of the subject
 * @returns {string} - a properly formatted subject name
 * @example
 * getSubjectName({ short_name: "Federal Regulations", abbreviation: "CFR", full_name: "Code of Federal Regulations" }) // "Federal Regulations"
 */
const getSubjectName = (subject) =>
    subject?.short_name || subject?.abbreviation || subject?.full_name;

/**
 * @param subject {Object} - a subject
 * @param subject.short_name {string | null} - the short name of the subject
 * @param subject.abbreviation {string | null} - the abbreviation of the subject
 * @param subject.full_name {string} - the full name of the subject
 * @typedef {[string, boolean]} NamePartTuple - an array containing a name (string or null) at index 0 and a boolean indicating whether it should be bolded at index 1
 * @returns {Array<NamePartTuple>} - an array of NamePartTuples
 * @example
 * getSubjectNameParts({ short_name: null, abbreviation: "CFR", full_name: "Code of Federal Regulations" }) // [["CFR", true], ["Code of Federal Regulations", false]]
 * getSubjectNameParts({ short_name: "Federal Regulations", abbreviation: "CFR", full_name: "Code of Federal Regulations" }) // [["Federal Regulations", true], ["Code of Federal Regulations", false]]
 * getSubjectNameParts({ short_name: null, abbreviation: null, full_name: "Code of Federal Regulations" }) // [[null, false], ["Code of Federal Regulations", true]]
 */
const getSubjectNameParts = (subject) => {
    const returnArray = [];

    const shortOrAbbr = subject.short_name || subject.abbreviation;

    // [name, isBolded]
    returnArray[0] = [shortOrAbbr, !!shortOrAbbr];
    returnArray[1] = [subject.full_name, !shortOrAbbr];

    return returnArray;
};

/**
 * @param subjects {Array} - an array of subjects
 * @returns {Array} - an array of subjects sorted by name
 */
const sortSubjects = (a, b) => {
    const aName = getSubjectName(a).toLowerCase();
    const bName = getSubjectName(b).toLowerCase();

    if (aName < bName) return -1;
    if (aName > bName) return 1;

    return 0;
};

export {
    formatDate,
    getSubjectName,
    getSubjectNameParts,
    locationLabel,
    locationUrl,
    sortSubjects,
};
