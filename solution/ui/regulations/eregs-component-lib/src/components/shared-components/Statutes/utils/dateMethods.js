import isNull from "lodash/isNull";
import isUndefined from "lodash/isUndefined";

// SSA table column date methods

/**
 * @param {string} type - Label for the date
 * @param {string} date - Date to be formatted
 *
 * @returns {string} - Formatted date label or empty string
 */
const getDateLabel = ({ type, date }) => {
    if (
        isNull(type) ||
        isNull(date) ||
        isUndefined(type) ||
        isUndefined(date) ||
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
