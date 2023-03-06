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
    const url = apiURL.replace("/v2/", "/v3/"); // TODO remove this

    const result = await httpApiGetLegacy(
        `${url}title/${params.title}/part/${params.part}/history/${
            Object.keys(params)[2]
        }/${Object.values(params)[2]}`
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

const getTitles = async (apiUrl) => {
    const url = apiUrl.replace("/v2/", "/v3/");
    return httpApiGetLegacy(`${url}titles`);
};

const getParts = async (apiURL, title) => {
    const url = apiURL.replace("/v2/", "/v3/");
    return httpApiGetLegacy(`${url}title/${title}/parts`);
};

const v3GetSupplementalContent = async (
    apiURL,
    { locations, locationDetails = false }
) => {
    const url = apiURL.replace("/v2/", "/v3/"); // TODO remove this

    return httpApiGetWithPagination(
        `${url}resources/?${locations}&paginate=true&location_details=${locationDetails}`,
        {}, // params, default
        apiURL
    );
};

const v3GetFederalRegisterDocs = async (apiURL, { page = 1, pageSize = 3 }) => {
    const url = apiURL.replace("/v2/", "/v3/"); // TODO remove this

    return httpApiGetLegacy(
        `${url}resources/federal_register_docs?page=${page}&page_size=${pageSize}&paginate=true`,
        {}, // params, default
        apiURL
    );
};

const getSubpartTOC = async (apiURL, title, part, subPart) => {
    const url = apiURL.replace("/v2/", "/v3/"); // TODO remove this

    return httpApiGetLegacy(
        `${url}title/${title}/part/${part}/version/latest/subpart/${subPart}/toc`
    );
};

export {
    getLastParserSuccessDate,
    getSupplementalContentByCategory,
    v3GetSupplementalContent,
    v3GetFederalRegisterDocs,
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
    getSubpartTOC,
    getGovInfoLinks,
    getTitles,
    getParts,
};
