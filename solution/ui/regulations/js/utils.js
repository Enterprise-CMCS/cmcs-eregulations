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
    parseError,
};
