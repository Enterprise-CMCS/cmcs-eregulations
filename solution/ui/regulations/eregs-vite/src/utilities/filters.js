const locationLabel = (value) => {
    return value.type.toLowerCase() === "section"
        ? `${value.part}.${value.section_id}`
        : `${value.part} Subpart ${value.subpart_id}`;
};

const locationUrl = (value, partsList, partsLastUpdated, base) => {
    // getting parent and partDate for proper link to section
    // e.g. /42/433/Subpart-A/2021-03-01/#433-10
    // is not straightforward with v2.  See below.
    // Thankfully v3 will add "latest" for date
    // and will better provide parent subpart in resource locations array.
    const { part, section_id, type, title, subpart_id } = value;
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

export { locationLabel, locationUrl };
