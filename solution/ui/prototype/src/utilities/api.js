import _filter from "lodash/filter";
import _get from "lodash/get";
import _isBoolean from "lodash/isBoolean";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isObject from "lodash/isObject";
import _keys from "lodash/keys";
import _map from "lodash/map";
import { niceDate, parseError, delay } from "./utils";
import mockExisting from "../mock-data/existing";

//const apiPath = "https://f2qpfij2v0.execute-api.us-east-1.amazonaws.com/dev-331/v2";
const apiPath = "http://localhost:8000/v2";

let config = {
    apiPath,
    fetchMode: "cors",
    maxRetryCount: 2,
};

let token;
let decodedIdToken;
const authHeader = (tok) => ({
    Authorization: `Bearer ${tok}`,
    "Content-Type": "application/json",
});

function setIdToken(encId) {
    token = encId;
    console.log("token is: ", token);
}

function getDecodedIdToken() {
    return decodedIdToken;
}

function forgetIdToken() {
    token = undefined;
    decodedIdToken = undefined;
}

function configure(obj) {
    config = { ...config, ...obj };
}

function fetchJson(url, options = {}, retryCount = 0) {
    // see https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    let isOk = false;
    let httpStatus;

    const headers = {
        Accept: "application/json",
        "Content-Type": "application/json",
    };
    const body = {};
    const merged = {
        method: "GET",
        cache: "no-cache",
        mode: config.fetchMode,
        redirect: "follow",
        body,
        ...options,
        headers: { ...headers, ...options.headers },
    };

    if (merged.method === "GET") delete merged.body; // otherwise fetch will throw an error
    if (merged.params) {
        // if query string parameters are specified then add them to the URL
        // The merged.params here is just a plain JavaScript object with key and value
        // For example {key1: value1, key2: value2}

        // Get keys from the params object such as [key1, key2] etc
        const paramKeys = _keys(merged.params);

        // Filter out params with undefined or null values
        const paramKeysToPass = _filter(
            paramKeys,
            (key) => !_isNil(_get(merged.params, key))
        );
        const query = _map(
            paramKeysToPass,
            (key) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(
                    _get(merged.params, key)
                )}`
        ).join("&");
        url = query ? `${url}?${query}` : url;
    }

    return Promise.resolve()
        .then(() => fetch(url, merged))
        .catch((err) => {
            // this will capture network/timeout errors, because fetch does not consider http Status 5xx or 4xx as errors
            if (retryCount < config.maxRetryCount) {
                let backoff = retryCount * retryCount;
                if (backoff < 1) backoff = 1;

                return Promise.resolve()
                    .then(() =>
                        console.log(
                            `Retrying count = ${retryCount}, Backoff = ${backoff}`
                        )
                    )
                    .then(() => delay(backoff))
                    .then(() => fetchJson(url, options, retryCount + 1));
            }
            throw parseError(err);
        })
        .then((response) => {
            isOk = response.ok;
            httpStatus = response.status;
            return response;
        })
        .then((response) => {
            if (_isFunction(response.text)) return response.text();
            return response;
        })
        .then((text) => {
            let json;
            try {
                if (_isObject(text)) {
                    json = text;
                } else {
                    json = JSON.parse(text);
                }
            } catch (err) {
                if (httpStatus >= 400) {
                    if (
                        httpStatus >= 501 &&
                        retryCount < config.maxRetryCount
                    ) {
                        let backoff = retryCount * retryCount;
                        if (backoff < 1) backoff = 1;

                        return Promise.resolve()
                            .then(() =>
                                console.log(
                                    `Retrying count = ${retryCount}, Backoff = ${backoff}`
                                )
                            )
                            .then(() => delay(backoff))
                            .then(() =>
                                fetchJson(url, options, retryCount + 1)
                            );
                    }
                    throw parseError({
                        message: text,
                        status: httpStatus,
                    });
                } else {
                    throw parseError(
                        new Error("The server did not return a json response.")
                    );
                }
            }

            return json;
        })
        .then((json) => {
            if (_isBoolean(isOk) && !isOk) {
                throw parseError({ ...json, status: httpStatus });
            } else {
                return json;
            }
        });
}

// ---------- helper functions ---------------

function httpApiMock(verb, urlPath, { data, params, response } = {}) {
    console.log(`Performing an HTTP ${verb} to ${config.apiPath}/${urlPath}`);
    data && console.log("DATA: ", data);
    params && console.log("PARAMS: ", params);
    response && console.log("RESPONSE: ", response);
    return response;
}

function httpApiGet(urlPath, { params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "GET",
        headers: authHeader(token),
        params,
    });
}

function httpApiPost(urlPath, { data = {}, params } = {}) {
    console.log(data);
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "POST",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}

// eslint-disable-next-line no-unused-vars
function httpApiPut(urlPath, { data, params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "PUT",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}

// eslint-disable-next-line no-unused-vars
function httpApiDelete(urlPath, { data, params } = {}) {
    return fetchJson(`${config.apiPath}/${urlPath}`, {
        method: "DELETE",
        headers: authHeader(token),
        params,
        body: JSON.stringify(data),
    });
}

// ---------- api calls ---------------

const login = (username, password) => {
    return httpApiPost("Authentication/login", {
        data: { username, password },
    });
};

const statusCheck = () => {
    return httpApiGet("Authentication/Test");
};

const getLastUpdatedDate = async (title = "42") => {
    const reducer = (accumulator, currentValue) => {
        return currentValue.date > accumulator.date
            ? currentValue
            : accumulator;
    };

    const result = await httpApiGet(`title/${title}/existing`);

    return niceDate(_get(result.reduce(reducer), "date"));
};

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    configure,
    setIdToken,
    getDecodedIdToken,
    forgetIdToken,
    config,
    login,
    statusCheck,
    getLastUpdatedDate,
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};
