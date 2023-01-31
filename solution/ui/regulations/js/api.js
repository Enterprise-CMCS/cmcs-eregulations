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

import { delay, niceDate, parseError } from "./utils";

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
            params,
        },
        0, // retryCount, default
        apiPath
    );
}

async function httpApiGetWithPagination(urlPath, { params } = {}, apiPath) {
    let results = [];
    let url = urlPath;
    while (url) {
        /* eslint-disable no-await-in-loop */
        const response = await httpApiGetLegacy(url, { params }, apiPath);
        results = results.concat(response.results ?? []);
        url = response.next;
        /* eslint-enable no-await-in-loop */
    }

    return results;
}

// ---------- api calls ---------------
const getLastUpdatedDates = async (apiUrl, title = "42") => {
    const reducer = (accumulator, currentValue) => {
        // key by partname, value by latest date
        // if partname is not in accumulator, add it
        // if partname is in accumulator, compare the dates and update the accumulator
        currentValue.partName.forEach((partName) => {
            if (!accumulator[partName]) {
                accumulator[partName] = currentValue.date;
            } else if (currentValue.date > accumulator[partName]) {
                accumulator[partName] = currentValue.date;
            }
        });

        return accumulator;
    };

    const result = await httpApiGetLegacy(`${apiUrl}title/${title}/existing`);

    return result.reduce(reducer, {});
};

/**
 * Get formatted date of most recent successful run of the ECFR parser
 *
 * @param {string} apiUrl - version of API passed in from Django.  Ex: `/v2/` or `/v3/`
 * @param {Object} params - parameters needed for API call
 * @param {string} [params.title=42] - CFR title number.
 *
 * @returns {string} - date in `MMM DD, YYYY` format or "N/A" if no date available
 */
const getLastParserSuccessDate = async (apiURL, { title = "42" }) => {
    // manually adjust to v3 if needed
    const url = apiURL.replace("/v2/", "/v3/");

    const result = await httpApiGetLegacy(`${url}ecfr_parser_result/${title}`);
    return result.end ? niceDate(result.end.split("T")[0]) : "N/A";
};

/**
 * Get array of objects containing valid GovInfo docs years with links to the PDF files.
 *
 * @param {string} apiURL - URL of API passed in from Django.  Ex: `/v2/` or `/v3/`
 * @param {Object} params - parameters needed for API call
 * @param {string} params.title - CFR title number.
 * @param {string} params.part - CFR part numer within title.
 * @param {string} params.[("section"|"appendix"|"subpart")] - CFR idenfifier for node type.  Ex. for "section": "10"
 *
 * @returns {Array<{year: string, link: string}>}
 */
const getGovInfoLinks = async (apiURL, params) => {
    // manually adjust to v3 if needed
    const url = apiURL.replace("/v2/", "/v3/");

    const result = await httpApiGetLegacy(
        `${url}title/${params.title}/part/${params.part}/history/${
            Object.keys(params)[2]
        }/${Object.values(params)[2]}`
    );

    return result;
};

/**
 * Returns the result from the all_parts endpoint
 *
 * @returns {Array} - a list of objects that represent a part of title 42
 */

const getAllParts = async (apiUrl) =>
    httpApiGetLegacy(
        `${apiUrl}all_parts`,
        {}, // params, default
        apiUrl
    );

/**
 * Returns the result from the categories endpoint
 *
 * @returns {Array} - a list of objects that represent possible supp content categories and subcategories
 */

const getCategories = async (apiUrl) =>
    httpApiGetLegacy(
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

const getSupplementalContentByCategory = async (
    api_url,
    categories = [1, 2]
) => {
    const result = await httpApiGetLegacy(
        `${api_url}all_sup?category=${categories.join(
            "&category="
        )}&max_results=100`,
        {}, // params, default
        api_url
    );
    return result.filter((r) => r.supplemental_content.length);
};

const v3GetSupplementalContent = async (
    apiURL,
    { locations, locationDetails = false }
) => {
    // manually adjust to v3 if needed
    const url = apiURL.replace("/v2/", "/v3/");

    return httpApiGetWithPagination(
        `${url}resources/?${locations}&paginate=true&location_details=${locationDetails}`,
        {}, // params, default
        apiURL
    );
};

const v3GetFederalRegisterDocs = async (apiURL, { page = 1, pageSize = 3 }) => {
    // manually adjust to v3 if needed
    const url = apiURL.replace("/v2/", "/v3/");

    return httpApiGetLegacy(
        `${url}resources/federal_register_docs?page=${page}&page_size=${pageSize}&paginate=true`,
        {}, // params, default
        apiURL
    );
};

const getSubpartTOC = async (apiURL, title, part, subPart) => {
    const url = apiURL.replace("/v2/", "/v3/");

    return httpApiGetLegacy(
        `${url}title/${title}/part/${part}/version/latest/subpart/${subPart}/toc`
    );
};

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    getAllParts,
    getCategories,
    getLastUpdatedDates,
    getLastParserSuccessDate,
    getSectionObjects,
    getSubPartsForPart,
    getSupplementalContentLegacy,
    getSupplementalContentByCategory,
    v3GetSupplementalContent,
    v3GetFederalRegisterDocs,
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
    getSubpartTOC,
    getGovInfoLinks,
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};
