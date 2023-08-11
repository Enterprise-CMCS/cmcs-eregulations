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
const getDateLabel = ({ type=undefined, date=undefined }) => {
    if (_isUndefined(type) || _isUndefined(date)) return "";
    return `${type} ${date}`;
};

export { getDateLabel };
