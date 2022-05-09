// v1.0 - JS API

import _filter from "lodash/filter";
import _get from "lodash/get";
import _isBoolean from "lodash/isBoolean";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isObject from "lodash/isObject";
import _keys from "lodash/keys";
import _map from "lodash/map";
import localforage from "localforage";

import { delay, parseError } from "./utils";

const config = {
    fetchMode: "cors",
    maxRetryCount: 2,
};

localforage.config({
    name: "eregs-pilot",
    version: 1.0,
    storeName: "eregs_django_pilot", // Should be alphanumeric, with underscores.
});

let token;
const authHeader = (tok) => ({
    Authorization: `Bearer ${tok}`,
    "Content-Type": "application/json",
});

function fetchJson(url, options = {}, retryCount = 0, apiPath) {
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
        .then(() => localforage.getItem(url.replace(apiPath, merged.method)))
        .then((value) => {
            if (value && Date.now() < value.expiration_date) {
                console.log("CACHE HIT");
                return value;
            } else {
                console.log("CACHE MISS");
                return fetch(url, merged);
            }
        })
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
                    .then(() =>
                        fetchJson(url, options, retryCount + 1, apiPath)
                    );
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
                                fetchJson(url, options, retryCount + 1, apiPath)
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
                json.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
                localforage.setItem(url.replace(apiPath, merged.method), json);
                return json;
            }
        });
}

// ---------- cache helpers -----------

const getCacheKeys = async () => localforage.keys();

const removeCacheItem = async (key) => localforage.removeItem(key);

const getCacheItem = async (key) => localforage.getItem(key);

const setCacheItem = async (key, data) => {
    data.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
    return localforage.setItem(key, data);
};

// ---------- helper functions ---------------
function httpApiGetLegacy(urlPath, { params } = {}, apiPath) {
    return fetchJson(
        `${urlPath}`,
        {
            method: "GET",
            headers: authHeader(token),
            params,
        },
        0, // retryCount, default
        apiPath
    );
}

// ---------- api calls ---------------


/**
 * Returns the result from the all_parts endpoint
 *
 * @returns {Array} - a list of objects that represent a part of title 42
 */

const getAllParts = async (apiUrl) => httpApiGetLegacy(
    `${apiUrl}all_parts`,
    {}, // params, default
    apiUrl
);

/**
 * Returns the result from the categories endpoint
 *
 * @returns {Array} - a list of objects that represent possible supp content categories and subcategories
 */

const getCategories = async (apiUrl) => httpApiGetLegacy(
    `${apiUrl}categories`,
    {}, // params, default
    apiUrl
);

/**
 *
 * Fetches all_parts and returns a list of objects for the subparts in that part
 * Each object has a label and an identifier
 * @param {string} apiUrl - api url from django environment
 * @param {string} part - the name of a part in title 42
 * @returns {Object<{label:string, identifier:string}>}
 */
const getSubPartsForPart = async (apiUrl, part) => {
    // if part is string of multiple parts, use final part
    part = part.indexOf(",") > 0 ? part.split(",").pop() : part;
    const all_parts = await getAllParts(apiUrl);
    const parts = all_parts.map((d) => d.name);
    const potentialSubParts =
        all_parts[parts.indexOf(part)].structure.children[0].children[0]
            .children[0].children;
    const subParts = potentialSubParts.filter((p) => p.type === "subpart");
    return subParts.map((s) => {
        return {
            label: s.label,
            identifier: s.identifier[0],
            range: s.descendant_range,
        };
    });
};

/**
 *
 * Fetches all_parts and returns formatted section objects for the part (and subpart if specified)
 * @param {string} apiUrl - api url from django environment
 * @param {string} part - a part in title 42
 * @param {?string} subPart - a subpart in title 42 ("A", "B", etc) - undefined returns all sections for part
 * @returns {Array[Object]} - an array of formatted objects for the section or subpart
 */
const getSectionObjects = async (apiUrl, part, subPart) => {
    // if part is string of multiple parts, use final part
    part = part.indexOf(",") > 0 ? part.split(",").pop() : part;
    const all_parts = await getAllParts(apiUrl);
    const parts = all_parts.map((d) => d.name);
    const potentialSubParts =
        all_parts[parts.indexOf(part)].structure.children[0].children[0]
            .children[0].children;
    if (subPart) {
        const parent = potentialSubParts.find(
            (p) => p.type === "subpart" && p.identifier[0] === subPart
        );
        return parent.children.map((c) => {
            return {
                identifier: c.identifier[1],
                label: c.label_level,
                description: c.label_description,
            };
        });
    } else {
        return potentialSubParts
            .filter((p) => p.type === "subpart")
            .flatMap((p) =>
                p.children.map((c) => {
                    return {
                        identifier: c.identifier[1],
                        label: c.label_level,
                        description: c.label_description,
                    };
                })
            );
    }
};

const getSupplementalContentLegacy = async (
    api_url,
    title = "42",
    part,
    joined_locations
) => {
    const result = await httpApiGetLegacy(
        `${api_url}title/${title}/part/${part}/supplemental_content?${joined_locations}`,
        {}, // params, default
        api_url
    );
    return result;
};


/**
 *
 * @param title {string} - The requested title, defaults to 42
 * @param part {string} - The part of the title
 * @param sections {Array[string]} - a list of the sections desired ([1,2,3...)
 * @param subparts {Array[string]} - a list of the subparts desired (subpart=A&subpart=B...)
 * @param q {string} - a word or phrase on which to search ("therapy")
 * @returns {Array[Object]} - a structured list of categories, subcategories and associated supplemental content
 */
const getSupplementalContentNew = async (
    title,
    part,
    sections = [],
    subparts = [],
    start = 0,
    max_results = 10000,
    q = "",
) => {
    const queryString = q ? `&q=${q}` : "";
    let sString = "";
    for (let s in sections) {
        sString = sString + "&sections=" + sections[s];
    }
    for (let sp in subparts) {
        sString = sString + "&subparts=" + subparts[sp];
    }
    sString = sString + "&start=" + start + "&max_results=" + max_results + queryString;
    const result = await httpApiGet(
        `title/${title}/part/${part}/supplemental_content?${sString}`
    );

    return result;
};

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    getAllParts,
    getCategories,
    getSectionObjects,
    getSubPartsForPart,
    getSupplementalContentLegacy,
    getSupplementalContentNew,
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};
