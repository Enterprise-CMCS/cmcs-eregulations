import _filter from "lodash/filter";
import _get from "lodash/get";
import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isObject from "lodash/isObject";
import _isUndefined from "lodash/isUndefined";
import _keys from "lodash/keys";
import _map from "lodash/map";
import _set from "lodash/set";
import _setWith from "lodash/setWith";
import _sortedUniq from "lodash/sortedUniq";
import localforage from "localforage";

import { delay, getKebabDate, niceDate, parseError } from "./utils";

const apiPath = `${process.env.VUE_APP_API_URL}/v2`;

let config = {
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

    return (
        Promise.resolve()
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
                            new Error(
                                "The server did not return a json response."
                            )
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
                    localforage.setItem(
                        url.replace(apiPath, merged.method),
                        json
                    );
                    return json;
                }
            })
    );
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
// ---------- cache helpers -----------

const getCacheKeys = async () => {
    return localforage.keys();
};

const removeCacheItem = async (key) => {
    return localforage.removeItem(key);
};

const getCacheItem = async (key) => {
    return localforage.getItem(key);
};

const setCacheItem = async (key, data) => {
    data.expiration_date = Date.now() + 8 * 60 * 60 * 1000; // 24 hours * 60 minutes * 60 seconds * 1000
    return localforage.setItem(key, data);
};

// ---------- api calls ---------------
const getLastUpdatedDate = async (title = "42") => {
    const reducer = (accumulator, currentValue) => {
        return currentValue.date > accumulator.date
            ? currentValue
            : accumulator;
    };

    const result = await httpApiGet(`title/${title}/existing`);

    return niceDate(_get(result.reduce(reducer), "date"));
};
/**
 *
 * Fetches a list of the part names for the desired title
 * @param title {string} - The title requested defaults to 42
 * @returns {Array} - A sorted list of the parts in this title
 */
const getPartNames = async (title = "42") => {
    const result = await httpApiGet(`title/${title}/existing`);

    return _sortedUniq(result.flatMap((part) => part.partName).sort());
};

/**
 *
 * Fetches the data and formats it for the home page
 *
 * @returns {Array[Object]} - a structured list used to populate the home page
 */
const getHomepageStructure = async () => {
    const reducer = (accumulator, currentValue) => {
        const title = currentValue.title;
        const chapter = _get(
            currentValue,
            "structure.children[0].identifier[0]"
        );
        const subchapter = _get(
            currentValue,
            "structure.children[0].children[0].identifier[0]"
        );
        const part = _get(
            currentValue,
            "structure.children[0].children[0].children[0].identifier[0]"
        );
        const partLabel = _get(
            currentValue,
            "structure.children[0].children[0].children[0].label"
        );
        const partDescription = _get(
            currentValue,
            "structure.children[0].children[0].children[0].label_description"
        );

        if (
            _isUndefined(title) ||
            _isUndefined(chapter) ||
            _isUndefined(subchapter) ||
            _isUndefined(part)
        ) {
            return accumulator;
        }

        const contentToSet = {
            title,
            chapter,
            subchapter,
            part,
            label: partLabel,
            description: partDescription,
            type: "part",
        };

        _setWith(
            accumulator,
            `${title}.chapters.${chapter}.subchapters.${subchapter}.parts.${part}`,
            contentToSet,
            Object
        );

        // if no title label, set it
        if (_isUndefined(accumulator[title].label)) {
            _set(
                accumulator,
                `${title}.label`,
                _get(currentValue, "structure.label")
            );
            _set(
                accumulator,
                `${title}.type`,
                _get(currentValue, "structure.type")
            );
        }

        // if no chapter label, set it
        if (_isUndefined(accumulator[title].chapters[chapter].label)) {
            _set(
                accumulator,
                `${title}.chapters.${chapter}.label`,
                _get(currentValue, "structure.children[0].label")
            );
            _set(
                accumulator,
                `${title}.chapters.${chapter}.type`,
                _get(currentValue, "structure.children[0].type")
            );
        }

        // if no subchapter label, set it
        if (
            _isUndefined(
                accumulator[title].chapters[chapter].subchapters[subchapter]
                    .label
            )
        ) {
            _set(
                accumulator,
                `${title}.chapters.${chapter}.subchapters.${subchapter}.label`,
                _get(currentValue, "structure.children[0].children[0].label")
            );
            _set(
                accumulator,
                `${title}.chapters.${chapter}.subchapters.${subchapter}.type`,
                _get(currentValue, "structure.children[0].children[0].type")
            );
        }

        return accumulator;
    };

    const result = await getAllParts()

    const transformedResult = result.reduce(reducer, {});

    return transformedResult;
};

/**
 * Returns the result from the all_parts endpoint
 *
 * @returns {Array} - a list of objects that represent a part of title 42
 */

const getAllParts = async () => {
    return await httpApiGet("all_parts");
}

/**
 *
 * Fetches all_parts and returns a list of those parts by name
 *
 * @returns {Array[string]} - a list pf parts for title 42
 */
const getPartsList = async () => {
    const all_parts = await getAllParts()
    return all_parts.map(d => d.name)
}

const getPartsDetails = async () => {
    const all_parts = await getAllParts()
    return all_parts.map(part => { return { 'id': part.name, 'name': part.structure.children[0].children[0].children[0].label } })
}
const getSubPartsandSections = async () => {
    const all_parts = await getAllParts()
    let subparts = []
    let fullSelection = []

    all_parts.forEach(part =>

        part.structure.children[0].children[0].children[0].children.forEach(subpart => subparts.push({ part: part.name, data: subpart })))

    for (const subpart in subparts) {
        fullSelection.push({ label: "Part " + subparts[subpart].part + " " + subparts[subpart].data.label, label: "Part " + subparts[subpart].part + " " + subparts[subpart].data.label, location: {part: subparts[subpart].part ,subpart: subparts[subpart].data.identifier[0]},type:'subpart'})

        let sections = subparts[subpart].data.children

        for (const section in sections) {
            fullSelection.push({ label: sections[section].label, id:sections[section].label, location:{ part: subparts[subpart].part , section : sections[section].identifier[1]}, part: subparts[subpart].part, type:'section'})
        }
    }


    return fullSelection
    //potentialSubParts = all_parts[parts.indexOf('400')].structure.children[0].children[0].children[0].children

}

/**
 *
 * Fetches all_parts and returns a list of objects for the subparts in that part
 * Each object has a label and an identifier
 * @param {string} - the name of a part in title 42
 * @returns {Object<{label:string, identifier:string}>}
 */
const getSubPartsForPart = async (part) => {
    const all_parts = await getAllParts()
    const parts = all_parts.map(d => d.name)
    const potentialSubParts = all_parts[parts.indexOf(part)].structure.children[0].children[0].children[0].children
    const subParts = potentialSubParts.filter(p => p.type === "subpart")
    return subParts.map(s =>{ return {label:s.label, identifier: s.identifier[0]}})
}

/**
 *
 * Fetches all_parts and returns a list of sections for the part and subpart specified
 * @param part - a part in title 42
 * @param subPart - a subpart in title 42 ("A", "B", etc)
 * @returns {Array[string]} - a list of all sections in this subpart
 */
const getSectionsForSubPart = async (part, subPart) => {
    const all_parts = await getAllParts()
    const parts = all_parts.map(d => d.name)
    const potentialSubParts = all_parts[parts.indexOf(part)].structure.children[0].children[0].children[0].children
    const parent = potentialSubParts.find(p => p.type === "subpart" && p.identifier[0] === subPart)
    const sections = []
    parent.children.forEach(c => {
        if (c.type === "section"){
            sections.push(c.identifier[1])
        }else if (c.children){
            c.children.forEach( child => {
                if (child.type === "section"){
                    sections.push(child.identifier[1])
                }
            })
        }
    })
    return sections

}

/**
 *
 * Fetches all_parts and returns a list of sections for the part and subpart specified
 * @param part - a part in title 42
 * @param subPart - a subpart in title 42 ("A", "B", etc)
 * @returns {Array[Object>TOC>, Object<orphansAndSubparts>]} - a tuple with a Table of contents and a list of
 * top level elements for the requested part
 */

const getPart = async (title, part) => {
    const result = await httpApiGet(
        `${getKebabDate()}/title/${title}/part/${part}`
    );

    // mixing lodash get and optional chaining.  Both provide safeguards and do the same this
    const toc = result?.toc;

    const orphansAndSubparts = _get(result, "document.children");
    return [toc, orphansAndSubparts];
};

/**
 *
 * @param title {string} - The requested title, defaults to 42
 * @param part {string} - The part pf the title
 * @param scope {string} - a formatted string of the sections desired ( section=1&section=2&section=3...)
 * @param identifier {string} - a formatted string of the subparts desired (subpart=A&subpart=B...)
 * @returns {Array[Object]} - a structured list of categories, subcategories and associated supplemental content
 */

const getAllSupplementalContentByPieces = async(start, max_results=100)=>{
    console.log('hi')
    const result = await(httpApiGet(`all_sup?&start=${start}&max_results=${max_results}`))
    return result;
}

const getSupplementalContent = async (
    title = "42",
    part,
    scope,
    identifier
) => {
    const result = await httpApiGet(
        `title/${title}/part/${part}/supplemental_content?&${scope}s=${identifier}`
    );
    return result;
};

/**
 *
 * @param title {string} - The requested title, defaults to 42
 * @param part {string} - The part pf the title
 * @param sections {Array[string]} - a list of the sections desired ([1,2,3...)
 * @param subparts {Array[string]} - a list of the subparts desired (subpart=A&subpart=B...)
 * @returns {Array[Object]} - a structured list of categories, subcategories and associated supplemental content
 */
const getSupplementalContentNew = async (
    title,
    part,
    sections = [],
    subparts = [],
    start=0,
    max_results=10000
) => {
    let sString = '';
    for (let s in sections) {
        sString = sString + "&sections=" + sections[s]
    }
    for (let sp in subparts) {
        sString = sString + "&subparts=" + subparts[sp]
    }
    sString= sString+"&start="+start+"&max_results="+max_results
    const result = await httpApiGet(
        `title/${title}/part/${part}/supplemental_content?${sString}`
    );

    return result;
};

const getCategories = async () => {
    return await httpApiGet("categories");
}
/**
 *
 * @param part {string} - a regulation part
 * @returns {Object<string:number>} - an object where the keys represent the display name for each part and
 * the value is the count of how many pieces of supplemental content exist for that part.
 */
const getSupplementalContentCountForPart = async (part) => {
    const result = await httpApiGet(
        `supplemental_content_count_by_part?part=${part}`
    );
    return result;
}

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    configure,
    setIdToken,
    getDecodedIdToken,
    forgetIdToken,
    config,
    getLastUpdatedDate,
    getHomepageStructure,
    getPartNames,
    getAllParts,
    getSubPartsForPart,
    getPart,
    getCacheKeys,
    removeCacheItem,
    getCacheItem,
    setCacheItem,
    getSupplementalContent,
    getSupplementalContentNew,
    getPartsList,
    getSectionsForSubPart,
    getSupplementalContentCountForPart,
    getCategories,
    getPartsDetails,
    getSubPartsandSections,
    getAllSupplementalContentByPieces
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};
