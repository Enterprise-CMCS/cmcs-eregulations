import _filter from "lodash/filter";
import _get from "lodash/get";
import _isBoolean from "lodash/isBoolean";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isObject from "lodash/isObject";
import _keys from "lodash/keys";
import _map from "lodash/map";

import localforage from "localforage";

import { delay, getKebabDate, niceDate, parseError } from "./utils";

const apiPath = `${
    import.meta.env.VITE_ENV === "prod" &&
    window.location.host.includes("cms.gov")
        ? `https://${window.location.host}`
        : import.meta.env.VITE_API_URL || "http://localhost:8000"
}/v3`;

const config = {
    apiPath,
    fetchMode: "cors",
    maxRetryCount: 2,
};

localforage.config({
    name: "eregs",
    version: 1.0,
    storeName: "eregs_django", // Should be alphanumeric, with underscores.
});

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
                json.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
                localforage.setItem(url.replace(apiPath, merged.method), json);
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

// use when components used directly in Django templates
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

async function httpApiGetWithPagination(urlPath, { params } = {}) {
    let results = [];
    let url = `${config.apiPath}/${urlPath}`;
    while (url) {
        /* eslint-disable no-await-in-loop */
        const response = await fetchJson(url, {
            method: "GET",
            headers: authHeader(token),
            params,
        });
        results = results.concat(response.results ?? []);
        url = response.next;
        /* eslint-enable no-await-in-loop */
    }
    return results;
}

function httpApiPost(urlPath, { data = {}, params } = {}) {
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
// ---------- cache helpers -----------

const getCacheKeys = async () => localforage.keys();

const removeCacheItem = async (key) => localforage.removeItem(key);

const getCacheItem = async (key) => localforage.getItem(key);

const setCacheItem = async (key, data) => {
    data.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
    return localforage.setItem(key, data);
};

// ---------- api calls ---------------
const getPartTOC = async (title, part) =>
    httpApiGet(`title/${title}/part/${part}/version/latest/toc`);

const getCategories = async (apiUrl) => {
    if (apiUrl) {
        return httpApiGetLegacy(`${apiUrl}resources/categories`);
    }

    return httpApiGet("resources/categories");
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
    const result = await httpApiGetLegacy(`${apiURL}ecfr_parser_result/${title}`);
    return result.end ? niceDate(result.end.split("T")[0]) : "N/A";
};
/**
 * @param {string} [apiUrl] - API base url passed in from Django template when component is used in Django template
 *
 * @returns {Promise<Array<number>>} - Promise that contains array of title numbers when fulfilled
 */
const getTOC = async ({title, apiUrl}) => {
    if (apiUrl) {
        return httpApiGetLegacy(
            title ? `${apiUrl}title/${title}/toc` : `${apiUrl}toc`
        );
    }

    return httpApiGet(title ? `title/${title}/toc` : `toc`);
};

const getSectionsForPart = async (title, part) =>
    httpApiGet(`title/${title}/part/${part}/version/latest/sections`);

const getSubpartTOC = async (title, part, subPart) =>
    httpApiGet(
        `title/${title}/part/${part}/version/latest/subpart/${subPart}/toc`
    );

const getSynonyms = async (query) =>
    httpApiGet(`synonyms?q=${encodeURIComponent(query)}`);

/* @param {string} apiUrl - API base url passed in from Django template when component is used in Django template
 * @param {Array<string>} [titleArr=["42"]] - Array of titlesto map over.
 *
 * @returns {Object.<string, string>} - Object with Part numbers as keys and YYYY-MM-DD datestring as values
 */
const getLastUpdatedDates = async (apiUrl, titleArr = ["42"]) => {
    const results = await Promise.all(
        titleArr.map((title) => httpApiGet(`title/${title}/parts`))
    );

    const combinedResults = results.flat(1).reduce(
        (accumulator, current) => ({
            ...accumulator,
            [current.name]: current,
        }),
        {}
    );

    // remove artifact added by front end caching
    delete combinedResults.expiration_date;

    return Object.fromEntries(
        Object.entries(combinedResults).map((arr) => [arr[1].name, arr[1].date])
    );
};
/**
 * Gets the three most recent resources of a type.
 * @param {*} apiURL - base url for the api
 * @param {*} type  - type of resource, fr doc or not
 * @returns 3 resources
 */
const getRecentResources = async (apiURL, { page = 1, pageSize = 3, type = "rules", categories }) => {
    if (type !== "rules") {
        return httpApiGetLegacy(
            `${apiURL}resources/supplemental_content?page=${page}&page_size=${pageSize}&paginate=true${categories}`,
            {}, // params, default
            apiURL
        );
    }
    return httpApiGetLegacy(
        `${apiURL}resources/federal_register_docs?page=${page}&page_size=${pageSize}&paginate=true`,
        {}, // params, default
        apiURL
    );
};

/**
 *
 * Fetches and formats list of parts to be used as dictionary
 * to create links to reg text in "related sections" part of
 * resources result item
 *
 * @returns {Array<{label: string, identifier: string, section: <Object>}>}
 */
const getFormattedPartsList = async (title = "42") => {
    const TOC = await getTOC({title});
    const partsList = TOC.children[0].children
        .map((subChapter) =>
            subChapter.children.map((part) => ({
                label: part.label,
                name: part.identifier[0],
            }))
        )
        .flat(1);

    const formattedPartsList = await Promise.all(
        partsList.map(async (part) => {
            const newPart = JSON.parse(JSON.stringify(part));
            const PartToc = await getPartTOC(title, part.name);
            const sections = {};
            PartToc.children
                .filter((TOCpart) => TOCpart.type === "subpart")
                .forEach((subpart) => {
                    subpart.children
                        .filter((section) => section.type === "section")
                        .forEach((c) => {
                            sections[c.identifier[c.identifier.length - 1]] =
                                c.parent[0];
                        });
                });
            newPart.sections = sections;
            return newPart;
        })
    );

    return formattedPartsList;
};

/**
 *
 * Fetches all_parts and returns a list of objects for the subparts in that part
 * Each object has a label and an identifier
 * @param {string} - the name of a part in title 42
 * @returns {Object<{label:string, identifier:string}>}
 */
const getSubPartsForPart = async (partParam, title = "42") => {
    // if part is string of multiple parts, use final part
    const selectedParts = partParam.split(",");
    const partTocs = await Promise.all(
        selectedParts.map(async (part) => getPartTOC(title, part))
    );
    return partTocs
        .map((partToc) =>
            partToc.children
                .filter((sp) => sp.type === "subpart")
                .map((subpart) => ({
                    label: subpart.label,
                    range: subpart.descendant_range,
                    part: subpart.parent[0],
                    identifier: subpart.identifier[0],
                }))
        )
        .flat(1);
};

/**
 *
 */
const getRegSearchResults = async ({
    q = "",
    paginate = true,
    page = 1,
    page_size = 100,
}) => {
    const response = await httpApiGet(
        `search?q=${encodeURIComponent(
            q
        )}&paginate=${paginate}&page_size=${page_size}&page=${page}`
    );

    return response;
};

const getSupplementalContent = async ({
    partDict,
    title,
    categories,
    q = "",
    start,
    maxResults = 1000,
    paginate = true,
    page = 1,
    catDetails = true,
    pageSize = 100,
    locationDetails = true,
    sortMethod = "newest",
    frGrouping = true,
    builtLocationString = "",
    apiUrl = ""
}) => {
    const queryString = q ? `&q=${encodeURIComponent(q)}` : "";
    let sString = "";

    if (partDict === "all") {
        sString = title ? `${sString}&locations=${title}` : "";
    } else if (builtLocationString !== "") {
        sString = `${sString}&${builtLocationString}`;
    } else {
        Object.keys(partDict).forEach((partKey) => {
            const part = partDict[partKey];
            part.subparts.forEach((subPart) => {
                sString = `${sString}&locations=${part.title}.${partKey}.${subPart}`;
            });
            part.sections.forEach((section) => {
                sString = `${sString}&locations=${part.title}.${partKey}.${section}`;
            });
            if (part.sections.length === 0 && part.subparts.length === 0) {
                sString = `${sString}&locations=${part.title}.${partKey}`;
            }
        });
    }

    if (categories) {
        const catList = await getCategories();
        categories.forEach((category) => {
            sString = `${sString}&categories=${
                catList.find((x) => x.name === category).id
            }`;
        });
    }

    sString = `${sString}&category_details=${catDetails}`;
    sString = `${sString}&location_details=${locationDetails}`;
    sString = `${sString}&start=${start}&max_results=${maxResults}${queryString}`;
    sString = `${sString}&sort=${sortMethod}`;
    if(paginate){
        sString = `${sString}&paginate=${paginate}&page_size=${pageSize}&page=${page}`;  
    }
    sString = `${sString}&fr_grouping=${frGrouping}`;

    let response = "";
    if (!apiUrl) {
        response = await httpApiGetLegacy(`${apiUrl}resources/?${sString}`);
    } else {
        response = await httpApiGet(`resources/?${sString}`);
    }
    return response;
};

/**
 * @param {string} [page=1] - page number of paginated results to return.
 * @param {string} [q=""] - search querystring
 *
 * @returns {Promise<{count: number, next: string, previous: string, results: Array<Object>}>} - Promise that contains response object when fulfilled
 */
const getSearchGovResources = async ({ page = 1, q = "" }) =>
    httpApiGet(`resources/search?q=${encodeURIComponent(q)}&page=${page}`);

/**
 * @param {string} [apiUrl] - API base url passed in from Django template when component is used in Django template
 *
 * @returns {Promise<Array<number>>} - Promise that contains array of title numbers when fulfilled
 */
const getTitles = async (apiUrl) => {
    if (apiUrl) {
        return httpApiGetLegacy(`${apiUrl}titles`);
    }

    return httpApiGet("titles");
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
    const result = await httpApiGetLegacy(
        `${apiURL}title/${params.title}/part/${params.part}/history/${
            Object.keys(params)[2]
        }/${Object.values(params)[2]}`
    );

    return result;
};

/**
 * @param {string} title - Title number.  Ex: `42` or `45`
 * @param {string} [apiUrl] - API base url passed in from Django template when component is used in Django template
 *
 * @returns {Promise <Array<{date: string, depth: number, id: number, last_updated: string, name: string}>} - Promise that contains array of part objects for provided title when fulfilled
 */
const getParts = async (title, apiUrl) => {
    if (apiUrl) {
        return httpApiGetLegacy(`${apiUrl}title/${title}/parts`);
    }
    return httpApiGet(`title/${title}/parts`);
};

export {
    config,
    configure,
    forgetIdToken,
    getCacheItem,
    getCacheKeys,
    getCategories,
    getDecodedIdToken,
    getFormattedPartsList,
    getLastUpdatedDates,
    getParts,
    getRecentResources,
    getRegSearchResults,
    getSearchGovResources,
    getSectionsForPart,
    getSubPartsForPart,
    getSubpartTOC,
    getSupplementalContent,
    getSynonyms,
    getTOC,
    getTitles,
    getPartTOC,
    removeCacheItem,
    setCacheItem,
    setIdToken,
    getLastParserSuccessDate,
    getGovInfoLinks,
};
