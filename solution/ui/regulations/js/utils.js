/* eslint-disable */
import _delay from "lodash/delay";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _isNil from "lodash/isNil";
import _isString from "lodash/isString";

// a promise friendly delay function
function delay(seconds) {
    return new Promise((resolve) => {
        _delay(resolve, seconds * 1000);
    });
}

// convert current date to YYYY-MM-DD
const getKebabDate = (date = new Date()) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    return `${year}-${month}-${day}`;
};

// YYYY-MM-DD to MMM DD, YYYY
const niceDate = (kebabDate) => {
    if (_isNil(kebabDate)) return "N/A";
    if (_isString(kebabDate) && _isEmpty(kebabDate)) return "N/A";
    const date = new Date(`${kebabDate}T12:00:00.000-05:00`);
    const month = date.toLocaleString("default", { month: "short" });
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month} ${day}, ${year}`;
};

function parseError(err) {
    console.log(err);
    const errMessage = err.errors
        ? err.errors[Object.keys(err.errors)[0]][0]
        : err.message;
    errMessage && alert(errMessage);

    const message = errMessage;
    try {
        const code = Object.keys(err.errors)[0];
        const status = _get(err, "status");
        const requestId = _get(err, "requestId");
        const error = new Error(message);
        error.code = code;
        error.requestId = requestId;
        error.root = err;
        error.status = status;

        return error;
    } catch {
        return new Error(message);
    }
}

export {
    delay,
    getKebabDate,
    niceDate,
    parseError,
};
