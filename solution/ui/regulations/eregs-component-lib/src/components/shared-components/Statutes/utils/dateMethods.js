/* eslint-disable camelcase */
/* eslint-disable eqeqeq */

import _isUndefined from "lodash/isUndefined";

// SSA table column date methods

/**
 * @param {string} type - Label for the date
 * @param {string} date - Date to be formatted
 *
 * @returns {string} - Formatted date label
 */
const getDateLabel = ({ type, date }) => {
    if (_isUndefined(type) || _isUndefined(date)) return "";

    const rawDate = new Date(date);
    const formattedDate = rawDate.toLocaleString("default", {
        month: "short",
        year: "numeric",
    });

    if (formattedDate == "Invalid Date") return "";

    return `${type} ${formattedDate}`;
};

export { getDateLabel };
