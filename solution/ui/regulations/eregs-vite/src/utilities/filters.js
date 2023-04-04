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

const locationLabel = ({ type, part, section_id, subpart_id }) => {
    return type.toLowerCase() === "section"
        ? `${part}.${section_id}`
        : `${part} Subpart ${subpart_id}`;
};

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
