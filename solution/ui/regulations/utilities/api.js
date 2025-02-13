import isBoolean from "lodash/isBoolean";
import isFunction from "lodash/isFunction";
import isNil from "lodash/isNil";
import isObject from "lodash/isObject";
import lodashFilter from "lodash/filter";
import lodashGet from "lodash/get";
import lodashKeys from "lodash/keys";
import lodashMap from "lodash/map";

import localforage from "localforage";

import { createLastUpdatedDates, delay, niceDate, parseError } from "./utils";
const DEFAULT_CACHE_RESPONSE = false; // Change this to true if needed

// still needed for caching purposes
const apiPath = `${
    import.meta.env.VITE_ENV === "prod" &&
    window.location.host.includes("cms.gov")
        ? `https://${window.location.host}`
        : import.meta.env.VITE_API_URL || "http://localhost:8000"
}/v3`;

let config = {
    fetchMode: "cors",
    maxRetryCount: 2,
};

localforage.config({
    name: "eregs",
    version: 1.0,
    storeName: "eregs_django", // Should be alphanumeric, with underscores.
});

const fetchJson = ({
    url,
    options = {},
    retryCount = 0,
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) => {
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
        const paramKeys = lodashKeys(merged.params);

        // Filter out params with undefined or null values
        const paramKeysToPass = lodashFilter(
            paramKeys,
            (key) => !isNil(lodashGet(merged.params, key))
        );
        const query = lodashMap(
            paramKeysToPass,
            (key) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(
                    lodashGet(merged.params, key)
                )}`
        ).join("&");
        url = query ? `${url}?${query}` : url;
    }

    return Promise.resolve()
        .then(() => {
            return fetch(url, merged);
        })
        .catch((err) => {
            // this will capture network/timeout errors, because fetch does not consider http Status 5xx or 4xx as errors
            if (retryCount < config.maxRetryCount) {
                let backoff = retryCount * retryCount;
                if (backoff < 1) backoff = 1;

                return Promise.resolve()
                    .then(() =>
                        console.info(
                            `Retrying count = ${retryCount}, Backoff = ${backoff}`
                        )
                    )
                    .then(() => delay(backoff))
                    .then(() =>
                        fetchJson({ url, options, retryCount: retryCount + 1 })
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
            if (isFunction(response.text)) return response.text();
            return response;
        })
        .then((text) => {
            let json;
            try {
                if (isObject(text)) {
                    json = text;
                } else {
                    json = JSON.parse(text);
                }
            } catch {
                if (httpStatus >= 400) {
                    if (
                        httpStatus >= 501 &&
                        retryCount < config.maxRetryCount
                    ) {
                        let backoff = retryCount * retryCount;
                        if (backoff < 1) backoff = 1;

                        return Promise.resolve()
                            .then(() =>
                                console.info(
                                    `Retrying count = ${retryCount}, Backoff = ${backoff}`
                                )
                            )
                            .then(() => delay(backoff))
                            .then(() =>
                                fetchJson({
                                    url,
                                    options,
                                    retryCount: retryCount + 1,
                                })
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
            if (isBoolean(isOk) && !isOk) {
                throw parseError({ ...json, status: httpStatus });
            } else {
                console.info("returning here!");
                return json;
            }
        });
};

// ---------- helper functions ---------------

/**
 * Get JSON data from an API endpoint using the GET method.
 * @param {string} urlPath - Path to the API endpoints
 * @param {Object} options - Object containing options for the request
 * @param {Object} [options.params] - Query string parameters to pass to the API
 * @param {boolean} [cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<Object>} - Promise that contains the JSON response when fulfilled
 * */
const httpApiGet = (
    urlPath,
    { params } = {},
    cacheResponse = DEFAULT_CACHE_RESPONSE
) => {
    return fetchJson({
        url: `${urlPath}`,
        options: {
            method: "GET",
            params,
        },
        retryCount: 0, // retryCount, default
        cacheResponse,
    });
};

// ---------- cache helpers -----------

const getCacheKeys = async () => localforage.keys();

const removeCacheItem = async (key) => localforage.removeItem(key);

const getCacheItem = async (key) => localforage.getItem(key);

const setCacheItem = async (key, data) => {
    data.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
    return localforage.setItem(key, data);
};

// ---------- api calls ---------------
/**
 * Get formatted date of most recent successful run of the ECFR parser
 *
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - version of API passed in from Django.  Ex: `/v2/` or `/v3/`
 * @param {string} [options.title=42] - CFR title number.
 *
 * @returns {string} - date in `MMM DD, YYYY` format or "N/A" if no date available
 */
const getLastParserSuccessDate = async ({ apiUrl, title = "42" }) => {
    const result = await httpApiGet(`${apiUrl}ecfr_parser_result/${title}`);
    return result.end ? niceDate(result.end.split("T")[0]) : "N/A";
};

/**
 * @typedef {Object} TocSection
 * @property {"title" | "chapter" | "subchapter" | "part"} type - The type of TOC entry.
 * @property {string} label - The full label/name of the TOC entry.
 * @property {string[]} parent - An array of parent identifiers (e.g., ["42"], ["IV"]).
 * @property {boolean} reserved - ???
 * @property {string[]} identifier - An array of identifiers for the section within its type (e.g., ["42"], ["IV"], ["400"]).
 * @property {string} label_level - A shortened form of the label that corresponds to the type identifier (e.g., "Title 42", "Part 400").
 * @property {"" | "title" | "chapter" | "subchapter"} parent_type - The type of the parent section.
 * @property {[string, string] | null} descendant_range - The range of descendant sections, if applicable.
 * @property {string} label_description - A shortened form of the label that corresponds to the description of the TOC entry.
 * @property {TocSection[]} children - An array of child TOC entries.
 */

/**
 * @param {Object} options - parameters needed for API calls
 * @param {string} [options.title] - Title number.  Ex: `42` or `45`
 * @param {string} [options.apiUrl] - API base url passed in from Django template when component is used in Django template
 * @returns {Promise<TocSection>} - Promise that contains object with TOC structure when fulfilled
 */
const getTOC = async ({ title, apiUrl }) =>
    httpApiGet(title ? `${apiUrl}title/${title}/toc` : `${apiUrl}toc`);

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template when component is used in Django template
 * @param {string} options.title - Title number.  Ex: `42` or `45`
 * @param {string} options.part - Part number within title.
 * @param {string} options.subPart - Subpart letter within part.
 * @returns {Promise<TocSection[]>} - Promise that contains object with TOC structure when fulfilled
 **/
const getSubpartTOC = async ({ apiUrl, title, part, subPart }) =>
    httpApiGet(
        `${apiUrl}title/${title}/part/${part}/version/latest/subpart/${subPart}/toc`
    );

/**
 * @typedef {Object} SynonymType
 * @property {string} baseWord - The base word for the synonym.
 * @property {boolean} isActive - Whether the synonym is active.
 * @property {SynonymType[]} synonyms - An array of synonyms for the base word.
 **/

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template when component is used in Django template
 * @param {string} options.query - Search query string.
 * @returns {Promise<SynonymType[]>} - Promise that contains array of synonyms when fulfilled
 **/
const getSynonyms = async ({ apiUrl, query }) =>
    httpApiGet(`${apiUrl}synonyms?q=${encodeURIComponent(query)}`);

/* @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template when component is used in Django template
 * @param {Array<string>} [options.titles=["42"]] - Array of titlesto map over.
 *
 * @returns {Object.<string, string>} - Object with Part numbers as keys and YYYY-MM-DD datestring as values
 */
const getLastUpdatedDates = async ({ apiUrl, titles = ["42"] }) => {
    const results = await Promise.all(
        titles.map((title) => httpApiGet(`${apiUrl}title/${title}/parts`))
    );

    return createLastUpdatedDates(results);
};

/**
 * Gets the three most recent resources of a type.
 * @param {string} apiURL - URL of API passed in from Django.  Ex: `/v2/` or `/v3/`
 * @param {Object} options - parameters needed for API call
 * @param {number} [options.page=1] - Page number to retrieve.
 * @param {number} [options.pageSize=3] - Number of items to retrieve.
 * @param {string} [options.type="rules"] - Type of resource to retrieve.  Ex: "rules" or "links"
 * @param {string} [options.categories] - Categories to filter by.
 * @returns {Promise<{count: number, next: ?string, previous: ?string, results: Array<Object>>} - Promise that contains array of resources when fulfilled
 */
const getRecentResources = async (
    apiURL,
    { page = 1, pageSize = 3, type = "rules", categories }
) => {
    if (type !== "rules") {
        return httpApiGet(
            `${apiURL}resources/public/links?page=${page}&page_size=${pageSize}${categories}`,
            {} // params, default
        );
    }
    return httpApiGet(
        `${apiURL}resources/public/federal_register_links?page=${page}&page_size=${pageSize}`,
        {} // params, default
    );
};

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {string} [options.q=""] - Search query string.
 * @param {boolean} [options.paginate=true] - Whether to paginate results.
 * @param {number} [options.page=1] - Page number to retrieve.
 * @param {number} [options.page_size=100] - Number of items to retrieve.
 * @returns {Promise<Object>} - Promise that contains search results when fulfilled
 */
const getRegSearchResults = async ({
    apiUrl,
    q = "",
    paginate = true,
    page = 1,
    page_size = 100,
}) => {
    const response = await httpApiGet(
        `${apiUrl}search?q=${encodeURIComponent(
            q
        )}&paginate=${paginate}&page_size=${page_size}&page=${page}`
    );

    return response;
};

/**
 * @param {Object} options - parameters needed for API call
 * @param {string|Object} options.partDict - Object containing part information or "all".
 * @param {string} options.title - Title number.
 * @param {string} [options.q=""] - Search query string.
 * @param {number} [options.page=1] - Page number to retrieve.
 * @param {number} [options.pageSize=100] - Number of items to retrieve.
 * @param {string} [options.sortMethod="newest"] - Method by which to sort results.
 * @param {string} [options.builtCitationString=""] - string of citations on which to filter
 * @param {string} [options.apiUrl=""] - API base url passed in from Django template
 * @returns {Promise<Object>} - Promise that contains supplemental content when fulfilled
 **/
const getSupplementalContent = async ({
    apiUrl = "",
    partDict,
    title,
    q = "",
    page = 1,
    pageSize = 100,
    sortMethod = "newest",
    builtCitationString = "",
}) => {
    const queryString = q ? `&q=${encodeURIComponent(q)}` : "";
    let sString = "";

    if (partDict === "all") {
        sString = title ? `${sString}&citations=${title}` : "";
    } else if (builtCitationString !== "") {
        sString = `${sString}&${builtCitationString}`;
    } else {
        Object.keys(partDict).forEach((partKey) => {
            const part = partDict[partKey];
            part.subparts.forEach((subPart) => {
                sString = `${sString}&citations=${part.title}.${partKey}.${subPart}`;
            });
            part.sections.forEach((section) => {
                sString = `${sString}&citations=${part.title}.${partKey}.${section}`;
            });
            if (part.sections.length === 0 && part.subparts.length === 0) {
                sString = `${sString}&citations=${part.title}.${partKey}`;
            }
        });
    }

    sString = `${sString}${queryString}&sort=${sortMethod}&page_size=${pageSize}&page=${page}`;

    return await httpApiGet(`${apiUrl}resources/public?${sString}`);
};

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @returns {Promise<Array<number>>} - Promise that contains array of title objects when fulfilled
 **/
const getTitles = async ({ apiUrl }) => httpApiGet(`${apiUrl}titles`);

/**
 * Get array of objects containing valid GovInfo docs years with links to the PDF files.
 *
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiURL - URL of API passed in from Django.  Ex: `/v2/` or `/v3/`
 * @param {Object} options.filterParams - Object containing filter parameters for the requestParams
 * @param {string} options.filterParams.title - CFR title number.
 * @param {string} options.filterParams.part - CFR part numer within title.
 * @param {string} options.filterParams.[("section"|"appendix"|"subpart")] - CFR idenfifier for node type.  Ex. for "section": "10"
 * @returns {Array<{year: string, link: string}>}
 */
const getGovInfoLinks = async ({ apiUrl, filterParams = {} }) =>
    await httpApiGet(
        `${apiUrl}title/${filterParams.title}/part/${
            filterParams.part
        }/history/${Object.keys(filterParams)[2]}/${
            Object.values(filterParams)[2]
        }`
    );

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.title - Title number.  Ex: `42` or `45`
 * @param {string} options.apiUrl - API base url passed in from Django template when component is used in Django template
 * @returns {Promise <Array<{date: string, depth: number, id: number, last_updated: Date, name: string}>} - Promise that contains array of part objects for provided title when fulfilled
 */
const getParts = async ({ title, apiUrl }) =>
    httpApiGet(`${apiUrl}title/${title}/parts`);

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template when component is used in Django template
 *
 * @returns {Promise <Array<{act: string, title: number, title_roman: string}>} - Promise that contains array of title objects when fulfilled
 */
const getStatutesActs = async ({ apiUrl }) => httpApiGet(`${apiUrl}acts`);

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} [options.act=Social Security Act] - Act on which to filter.
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {string} [options.title=19] - Act title number as digits.
 *
 * @returns {Promise <Array<{section: string, title: number, usc: string, act: string, name: string, statute_title: string, source_url: string}>} - Promise that contains array of part objects for provided title when fulfilled
 */
const getStatutes = async ({
    act = "Social Security Act",
    apiUrl,
    title = "19",
}) =>
    httpApiGet(
        `${apiUrl}statutes?act=${encodeURIComponent(act)}&title=${title}`
    );

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{count: number, next: ?string, previous: ?string, results: Array<{id: number, full_name: string, short_name: string, abbreviation: string, description: string, public_resources: number, internal_resources: number}>}>} - Promise that contains array of subjects when fulfilled
 */
const getSubjects = async ({
    apiUrl,
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(`${apiUrl}resources/subjects?page_size=1000`, {}, cacheResponse);

/**
 * An object representing an internal category
 * @typedef {Object} InternalCategory
 * @property {number} id - Category id
 * @property {string} name - Category name
 * @property {string} description - Category description
 * @property {number} order - Category order
 * @property {boolean} show_if_empty - Whether to show category if empty
 * @property {string} type - Category type
 * @property {number} [parent] - Parent category id
 * @property {InternalCategory[]} subcategories - Array of subcategories
 */

/**
 * Retrieves a top-down representation of internal categories, with each category containing zero or more sub-categories.
 *
 * @param {Object} options - An object containing options for the request.
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{counts: number, next: ?string, previous: ?string, results: InternalCategory[]}>} - Promise that contains array of categories when fulfilled
 */
const getInternalCategories = async ({
    apiUrl,
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(
        `${apiUrl}resources/internal/categories?page_size=1000`,
        {},
        cacheResponse
    );

/**
 * An object representing an external category
 * @typedef {Object} ExternalCategory
 * @property {number} id - Category id
 * @property {string} name - Category name
 * @property {string} description - Category description
 * @property {number} order - Category order
 * @property {boolean} show_if_empty - Whether to show category if empty
 * @property {boolean} is_fr_link_category - Whether category is a Federal Register link category
 * @property {string} type - Category type
 * @property {number} [parent] - Parent category id
 * @property {ExternalCategory[]} subcategories - Array of subcategories
 */

/**
 * Retrieves a top-down representation of external categories, with each category containing zero or more sub-categories.
 *
 * @param {object} options - An object containing options for the request.
 * @param {string} [options.apiUrl] - The base URL of the external API.
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - A boolean flag indicating whether to cache the API response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{counts: number, next: ?string, previous: ?string, results: ExternalCategory[]}>} - Promise that contains array of categories when fulfilled
 */
const getExternalCategories = async ({
    apiUrl,
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(
        `${apiUrl}resources/public/categories?page_size=1000`,
        {},
        cacheResponse
    );

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {string} [optons.requestParams] - Query string parameters to pass to API
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{count: number, next: ?string, previous: ?string, results: Array<Object>}>} - Promise that contains array of file items when fulfilled
 */
const getCombinedContent = async ({
    apiUrl,
    requestParams = "",
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(
        `${apiUrl}content-search/${requestParams ? `?${requestParams}` : ""}`,
        {},
        cacheResponse
    );

const getGranularCounts = async ({
    apiUrl,
    requestParams = "",
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(
        `${apiUrl}content-search/counts${requestParams ? `?${requestParams}` : ""}`,
        {},
        cacheResponse
    );

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {string} [options.requestParams] - Query string parameters to pass to API
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{count: number, next: ?string, previous: ?string, results: Array<Object>}>} - Promise that contains array of file items when fulfilled
 */
const getContentWithoutQuery = async ({
    apiUrl,
    requestParams = "",
    docType, // "public" or "internal"
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) => {
    const typeString = docType ? `${docType.toLowerCase()}` : "";
    const rqParams = requestParams ? `?${requestParams}` : "";

    return httpApiGet(
        `${apiUrl}resources/${typeString}${rqParams}`,
        {},
        cacheResponse
    );
};

/**
 * @param {Object} options - parameters needed for API call
 * @param {string} options.apiUrl - API base url passed in from Django template
 * @param {string} [options.requestParams] - Query string parameters to pass to API
 * @param {boolean} [options.cacheResponse=DEFAULT_CACHE_RESPONSE] - Whether to cache the response. Defaults to the value of `DEFAULT_CACHE_RESPONSE`.
 * @returns {Promise<{count: number, next: ?string, previous: ?string, results: Array<Object>}>} - Promise that contains array of file items when fulfilled
 */
const getInternalDocs = async ({
    apiUrl,
    requestParams = "",
    cacheResponse = DEFAULT_CACHE_RESPONSE,
}) =>
    httpApiGet(
        `${apiUrl}resources/internal${
            requestParams ? `?${requestParams}` : ""
        }`,
        {},
        cacheResponse
    );

const throwGenericError = async () =>
    new Promise((_resolve, reject) => {
        setTimeout(() => reject(new Error("Contrived error")), 2000);
    });

export {
    config,
    getCacheItem,
    getCacheKeys,
    getCombinedContent,
    getContentWithoutQuery,
    getExternalCategories,
    getGovInfoLinks,
    getGranularCounts,
    getInternalCategories,
    getInternalDocs,
    getSubjects,
    getLastParserSuccessDate,
    getLastUpdatedDates,
    getParts,
    getRecentResources,
    getRegSearchResults,
    getStatutes,
    getStatutesActs,
    getSubpartTOC,
    getSupplementalContent,
    getSynonyms,
    getTOC,
    getTitles,
    removeCacheItem,
    setCacheItem,
    throwGenericError,
};
