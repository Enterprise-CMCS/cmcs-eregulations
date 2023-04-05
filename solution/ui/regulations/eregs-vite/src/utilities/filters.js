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
 * @param partsList {Array<{label: {string}, name: {string}, sections: {Object}}>} - array of objects describing each part in the app
 * @param partsLastUpdated {Object} - object containing part numbers as keys and YYYY-MM-DD dates for values
 * @param base {string} - base to be prepended to returned URL
 * @returns {string} - URL to location
 */
const locationUrl = (
    { title, type, part, section_id, subpart_id },
    partsList,
    partsLastUpdated,
    base
) => {
    // getting parent and partDate for proper link to section
    // e.g. /42/433/Subpart-A/2021-03-01/#433-10
    // is not straightforward with v2.  See below.
    // Thankfully v3 will add "latest" for date
    // and will better provide parent subpart in resource locations array.
    const partDate = `${partsLastUpdated[part]}/`;

    // early return if related regulation is a subpart and not a section
    if (type.toLowerCase() === "subpart") {
        return `${base}${title}/${part}/Subpart-${subpart_id}/${partDate}`;
    }
    const partObj = partsList.find((parts) => parts.name == part);
    const subpart = partObj?.sections?.[section_id];

    // todo: Figure out which no subpart sections are invalid and which are orphans
    return subpart
        ? `${base}${title}/${part}/Subpart-${subpart}/${partDate}#${part}-${section_id}`
        : `${base}${title}/${part}/${partDate}#${part}-${section_id}`;
};

export { formatDate, locationLabel, locationUrl };
