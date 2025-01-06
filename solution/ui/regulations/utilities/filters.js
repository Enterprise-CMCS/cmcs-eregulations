/**
 * @param {string} dateString - a date string in YYYY-MM-DD format
 * @returns {string} - a date string in Month D/DD, YYYY format
 */
const formatDate = (dateString) => {
    if (!dateString || typeof dateString !== "string") {
        return "Invalid Date";
    }

    if (dateString.includes("/")) {
        return dateString;
    }

    const date = new Date(dateString);

    if (date.toString() === "Invalid Date") {
        return date.toString();
    }

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
 *
 * @param {Object} location - a Subpart or Section of the Regs
 * @param {string} location.type - the type of location (ex: Subpart, Section)
 * @param {string} location.part - the part number for the location
 * @param {?string} location.section_id - the section number
 * @param {?string} location.subpart_id - the subpart name
 * @returns {string} - a properly formatted label
 */
const locationLabel = ({ type, part, section_id, subpart_id }) => {
    if (!type || typeof type !== "string") {
        return "Invalid Location";
    }
    return type?.toLowerCase() === "section"
        ? `${part}.${section_id}`
        : `${part} Subpart ${subpart_id}`;
};

/**
 * @param {Object} location - a Subpart or Section of the Regs
 * @param {string} location.title - the title number of the location (ex: 42)
 * @param {string} location.type - the type of location (ex: Subpart, Section)
 * @param {string} location.part - the part number for the location
 * @param {?string} location.section_id - the section number
 * @param {?string} location.subpart_id - the subpart name
 * @param {string} base - base to be prepended to returned URL
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
 * @param {Object} subject - a subject
 * @param {?string} subject.short_name - the short name of the subject
 * @param {?string} subject.abbreviation - the abbreviation of the subject
 * @param {string} subject.full_name - the full name of the subject
 * @returns {string} - a properly formatted subject name
 * @example
 * getSubjectName({ short_name: "Federal Regulations", abbreviation: "CFR", full_name: "Code of Federal Regulations" }) // "Federal Regulations"
 */
const getSubjectName = (subject) =>
    subject?.short_name || subject?.abbreviation || subject?.full_name;

/**
 * @typedef {[name: string, isBolded: boolean]} NamePartTuple - an array containing a name (string or null) at index 0 and a boolean indicating whether it should be bolded at index 1
 *
 * @param {Object} subject - a subject
 * @param {?string} subject.short_name - the short name of the subject
 * @param {?string} subject.abbreviation - the abbreviation of the subject
 * @param {string} subject.full_name - the full name of the subject
 * @returns {NamePartTuple[]} - an array of NamePartTuples
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
 * @param {Object} a - a Subject
 * @param {Object} b - a Subject
 * @returns {number} - a number indicating the sort order of the two subjects
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
