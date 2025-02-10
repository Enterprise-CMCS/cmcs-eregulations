// SSA table column date methods

/**
 * @param {string} type - Label for the date
 * @param {string} date - Date to be formatted
 *
 * @returns {string} - Formatted date label or empty string
 */
const getDateLabel = ({ type, date }) => {
    if (
        type === null ||
        date === null ||
        type === undefined ||
        date === undefined ||
        type === ""
    )
        return "";

    const rawDate = new Date(date);
    // add a day to get correct month because Javascript dates are weird
    rawDate.setDate(rawDate.getDate() + 1);
    const formattedDate = rawDate.toLocaleString("default", {
        month: "short",
        year: "numeric",
    });

    if (formattedDate === "Invalid Date") return "";

    return `${type} ${formattedDate}`;
};

export { getDateLabel };
