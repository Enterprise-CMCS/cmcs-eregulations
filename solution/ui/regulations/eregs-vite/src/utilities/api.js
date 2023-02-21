import _filter from "lodash/filter";
import _get from "lodash/get";
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

const apiPath = `${
    import.meta.env.VITE_ENV === "prod" &&
    window.location.host.includes("cms.gov")
        ? `https://${window.location.host}`
        : import.meta.env.VITE_API_URL || "http://localhost:8000"
}`;
const apiPathV2 = `${apiPath}/v2`;
const apiPathV3 = `${apiPath}/v3`;

const config = {
    apiPath,
    apiPathV2,
    apiPathV3,
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
    return fetchJson(`${config.apiPathV2}/${urlPath}`, {
        method: "GET",
        headers: authHeader(token),
        params,
    });
}

function httpApiGetV3(urlPath, { params } = {}) {
    return fetchJson(`${config.apiPathV3}/${urlPath}`, {
        method: "GET",
        headers: authHeader(token),
        params,
    });
}

async function httpApiGetV3WithPagination(urlPath, { params } = {}) {
    let results = [];
    let url = `${config.apiPathV3}/${urlPath}`;
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
const getLastUpdatedDate = async (title = "42") => {
    const reducer = (accumulator, currentValue) => currentValue.date > accumulator.date
            ? currentValue
            : accumulator;

    const result = await httpApiGet(`title/${title}/existing`);

    return niceDate(_get(result.reduce(reducer), "date"));
};

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

    const result = await httpApiGet(`title/${title}/existing`);

    return result.reduce(reducer, {});
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
 * Returns the result from the all_parts endpoint
 *
 * @returns {Array} - a list of objects that represent a part of title 42
 */

const getAllParts = async () => httpApiGet("all_parts");

/**
 *
 * Fetches the data and formats it for the home page
 *
 * @returns {Array[Object]} - a structured list used to populate the home page
 */
const getHomepageStructure = async () => {
    const reducer = (accumulator, currentValue) => {
        const { title } = currentValue;

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

    const result = await getAllParts();

    const transformedResult = result.reduce(reducer, {});

    return transformedResult;
};

/**
 *
 * Fetches all_parts and returns a list of those parts by name
 *
 * @returns {Array<string>} - a list pf parts for title 42
 */
const getPartsList = async () => {
    const allParts = await getAllParts()
    return allParts.map(d => d.name)
}

/**
 *
 * Fetches and formats list of parts to be used as dictionary
 * to create links to reg text in "related sections" part of
 * resources result item
 *
 * @returns {Array<{label: string, identifier: string, section: <Object>}>}
 */
const getFormattedPartsList = async () => {
    const TOC = await getTOC();
    const partsList = TOC[0].children[0].children
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
            const PartToc = await getPartTOC(42, part.name);
            const sections = {};
            PartToc.children
                .filter((TOCpart) => TOCpart.type === "subpart")
                .forEach((subpart) => {
                    subpart.children
                        .filter((section) => section.type === "section")
                        .forEach((c) => {
                            sections[
                                c.identifier[c.identifier.length - 1]
                            ] = c.parent[0];
                        });
                });
            newPart.sections = sections;
            return newPart;
        })
    );

    return formattedPartsList;
}

const getPartsDetails = async () => {
    const allParts = await getAllParts()
    return allParts.map(part => { return { 'id': part.name, 'name': part.structure.children[0].children[0].children[0].label } })
}

const getSubPartsandSections = async () => {
    const allParts = await getAllParts()
    let subParts = []
    let fullSelection = []

    allParts.forEach(part =>
        part.structure.children[0].children[0].children[0].children.forEach(subpart => subParts.push({ part: part.name, data: subpart }
        )))

    subParts.forEach( subPart => {
        if (subPart.data.type === 'section') {
            fullSelection.push({ label: subPart.data.label, id: subPart.data.label, location: { part: subPart.part, section: subPart.data.identifier[1] }, type: 'section' })
        }
        else {
            const sections = subPart.data.children
            fullSelection.push({
                label: `Part ${  subPart.part  } ${  subPart.data.label}`,
                location: { part: subPart.part, subpart: subPart.data.identifier[0] },
                type: 'subpart'
            })

            sections.forEach(section => {
                if (section.type !== "subject_group") {
                    fullSelection.push({
                        label: section.label, id: section.label,
                        location: { part: subPart.part, section: section.identifier[1] },
                        part: subPart.part,
                        type: 'section'
                    })
                }
                else {
                    section.children.forEach( section => {
                        fullSelection.push({
                            label: section.label,
                            id: section.label,
                            location: {
                                part: subPart.part,
                                section: section.identifier[1]
                            },
                            part: subPart.part,
                            type: 'section'
                        })
                    })
                }
            })
        }
    })


    return fullSelection
    // potentialSubParts = all_parts[parts.indexOf('400')].structure.children[0].children[0].children[0].children

}

const getAllSections = async () => {
    const allParts = await getAllParts()
    const subParts = []
    const allSections = []

    allParts.forEach(
        part => part.structure.children[0].children[0].children[0].children.forEach(
            subpart => subParts.push({ part: part.name, data: subpart })
        )
    )
    subParts.forEach( subPart => {
        const {part} = subPart

        if (subPart.data.type === 'section') {
            allSections.push({
                part,
                subpart: 'none',
                identifier: subPart.data.identifier[1],
                label: subPart.data.label_level,
                description: subPart.data.label_description
            })
        }
        else {
            const sections = subPart.data.children
            const sub = subPart.data.identifier[0]

            sections.forEach( section => {

                if (section.type !== "subject_group") {
                    allSections.push({
                        part,
                        subpart: sub,
                        identifier: section.identifier[1],
                        label: section.label_level,
                        description: section.label_description })
                }
                else {
                    section.children.forEach( s => {
                        allSections.push({
                            part,
                            subpart: sub,
                            identifier: s.identifier[1],
                            label: s.label_level,
                            description: s.label_description })
                    })
                }
            })
        }
    })
    return allSections;
}
/**
 *
 * Fetches all_parts and returns a list of objects for the subparts in that part
 * Each object has a label and an identifier
 * @param {string} - the name of a part in title 42
 * @returns {Object<{label:string, identifier:string}>}
 */
const getSubPartsForPart = async (partParam) => {
    // if part is string of multiple parts, use final part
    const selectedParts = partParam.split(',')
    const partTocs = await Promise.all(selectedParts.map(async part => getPartTOC(42, part)))
    return partTocs.map(partToc =>
        partToc.children.filter(sp => sp.type === "subpart").map(subpart => ({
          label:subpart.label,
          range: subpart.descendant_range,
          part: subpart.parent[0],
          identifier: subpart.identifier[0]
        }))
    ).flat(1)
};

/**
 *
 * Fetches all_parts and returns a list of sections for the part and subpart specified
 * @param part - a part in title 42
 * @param subPart - a subpart in title 42 ("A", "B", etc)
 * @returns {Array[string]} - a list of all sections in this subpart
 */
const getSectionsForSubPart = async (part, subPart) => {
    const allParts = await getAllParts()
    const parts = allParts.map(d => d.name)
    const potentialSubParts = allParts[parts.indexOf(part)].structure.children[0].children[0].children[0].children
    const parent = potentialSubParts.find(p => p.type === "subpart" && p.identifier[0] === subPart)
    const sections = []
    parent.children.forEach(c => {
        if (c.type === "section" && !c.reserved) {
            sections.push(c.identifier[1])
        } else if (c.children) {
            c.children.forEach(child => {
                if (child.type === "section" && !c.reserved) {
                    sections.push(child.identifier[1])
                }
            })
        }
    })
    return sections
};

/**
 *
 * Fetches all_parts and returns formatted section objects for the part (and subpart if specified)
 * @param {string} part - a part in title 42
 * @param {?string} subPart - a subpart in title 42 ("A", "B", etc) - undefined returns all sections for part
 * @returns {Array[Object]} - an array of formatted objects for the section or subpart
 */
const getSectionObjects = async (part, subPart) => {
    // if part is string of multiple parts, use final part
    part = part.indexOf(",") > 0 ? part.split(",").pop() : part;
    const allParts = await getAllParts();
    const parts = allParts.map((d) => d.name);
    const potentialSubParts =
        allParts[parts.indexOf(part)].structure.children[0].children[0]
            .children[0].children;
    if (subPart) {
        const parent = potentialSubParts.find(
            (p) => p.type === "subpart" && p.identifier[0] === subPart
        );
        return parent.children.map((c) => {
            return {
                identifier: c.identifier[1],
                label: c.label_level,
                part,
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
                        part,
                        description: c.label_description,
                    };
                })
            );
    }
};

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

    const orphansAndSubParts = _get(result, "document.children");
    return [toc, orphansAndSubParts];
};

/**
 *
 * @param title {string} - The requested title, defaults to 42
 * @param part {string} - The part pf the title
 * @param scope {string} - a formatted string of the sections desired ( section=1&section=2&section=3...)
 * @param identifier {string} - a formatted string of the subparts desired (subpart=A&subpart=B...)
 * @returns {Array[Object]} - a structured list of categories, subcategories and associated supplemental content
 */

const getAllSupplementalContentByPieces = async (start, max_results = 100) => {
    const result = await (httpApiGet(`all_sup?&start=${start}&max_results=${max_results}`))
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
 */
const getRegSearchResults = async ({
    q = "",
    paginate = true,
    page = 1,
    page_size = 100,
}) => {
    const response = await httpApiGetV3(`search?q=${q}&paginate=${paginate}&page_size=${page_size}&page=${page}`);

    return response;
};

// search supplemental content with search.gov
const getSupplementalContentSearchGov = async ({
    q = "",
    key = 'M1igE4Qcfo8LLQr7o_I9KLA6qkybmlC9IRhVCCbFbl4=',
}) => {
    const response = await fetch(`https://search.usa.gov/api/v2/search/?affiliate=reg-pilot-cms-test&access_key=${key}&query=${q}`)
    console.log("The RESPONSE IS --->", response)
    const finalRes = await response.json();
    console.log("final results are",finalRes.web)
    const search = { results: []
    }
    finalRes.web.results.forEach((item) => {
       search.results.push({
           date: item.publication_date,
           description: item.snippet.replaceAll('','<strong>').replaceAll('','</strong>'),
           url: item.url,
           name:  item.title === '-' ? "" : item.title

       })
    })
    search.total = finalRes.web.total
    console.log('--> response results are', search)
    return search;
};

// todo: make these JS style camel case
const getSupplementalContentV3 = async (
    {
        partDict,
        categories,
        q = "",
        start,
        max_results = 1000,
        paginate = true,
        page = 1,
        cat_details = true,
        page_size = 100,
        location_details = true,
        sortMethod = "newest",
        fr_grouping = true,
    }
) => {
    const queryString = q ? `&q=${q}` : "";
    let sString = "";

    if (partDict === "all") {
        sString = ""
    }

    else {
        Object.keys(partDict).forEach(partKey => {
            const part = partDict[partKey]
            part.subparts.forEach(subPart => {
                sString = `${sString}&locations=${part.title}.${partKey}.${subPart}`
            })
            part.sections.forEach(section => {
                sString = `${sString}&locations=${part.title}.${partKey}.${section}`
            })
            if (part.sections.length === 0 && part.subparts.length === 0) {
                sString = `${sString}&locations=${part.title}.${partKey}`
            }
        })
    }

    if (categories) {
        const catList = await getCategories()
        categories.forEach(category => {
            sString = `${sString}&categories=${catList.find(x => x.name === category).id}`
        })
    }

    sString = `${sString}&category_details=${cat_details}`
    sString = `${sString}&location_details=${location_details}`
    sString = `${sString}&start=${start}&max_results=${max_results}${queryString}`;
    sString = `${sString}&sort=${sortMethod}`;

    sString = `${sString}&paginate=true&page_size=${page_size}&page=${page}`
    sString = `${sString}&fr_grouping=${fr_grouping}`
    const response = await httpApiGetV3(`resources/?${sString}`)
    return response;

}

const getSupIDByLocations = async () => {
    const result = await httpApiGet('locations');
    return result;
}

const getSupByPart = async (title, part, subparts, sections) => {
    const locations = await httpApiGet('locations');
    const allIndex = sections.concat(subparts)

    const supplemental = await httpApiGet(`sup_by_id/title/${title}/part/${part}`)

    const supList = allIndex.length === 0
        ? Object.keys(locations[title][part]).reduce((acc, x) => {
            return acc.concat(locations[title][part][x])
        }, [])
        : allIndex.reduce((acc, sec) => {
            return acc.concat(locations[title][part][sec])
        }, [])

    return [...new Set(supList)].map(supId => {
        const item = JSON.parse(JSON.stringify(supplemental[supId]))
        item.category = item.category.name
        return item
    })

}
const getCategories = async () =>  httpApiGetV3("resources/categories");

const getTOC = async (title) =>
    httpApiGetV3(title ? `title/${title}/toc` : `toc`);

const getPartTOC = async (title, part) =>  httpApiGetV3(`title/${title}/part/${part}/version/latest/toc`);

const getSectionsForPart = async (title, part) => httpApiGetV3(`title/${title}/part/${part}/version/latest/sections`)

const getSubpartTOC = async (title, part, subPart) => httpApiGetV3(`title/${title}/part/${part}/version/latest/subpart/${subPart}/toc`)

const getSynonyms = async(query) => httpApiGetV3(`synonym/${query}`);
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
};

/**
 *
 * @param query {string} - a query string to search supplemental content
 * @returns {Object<string:number>} - a list containing unstructured supplemental content search results
 */
const getSupplementalContentSearchResults = async (query) => {
    const result = await httpApiGet(
        `supplemental_content/search?q=${query}`
    );
    return result;
};

// API Functions Insertion Point (do not change this text, it is being used by hygen cli)

export {
    configure,
    setIdToken,
    getDecodedIdToken,
    forgetIdToken,
    config,
    getLastUpdatedDate,
    getLastUpdatedDates,
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
    getPartsList,
    getFormattedPartsList,
    getSectionsForSubPart,
    getSectionObjects,
    getSupplementalContentCountForPart,
    getCategories,
    getPartsDetails,
    getSubPartsandSections,
    getAllSupplementalContentByPieces,
    getSupIDByLocations,
    getSupByPart,
    getAllSections,
    getSupplementalContentV3,
    getSupplementalContentSearchResults,
    getTOC,
    getPartTOC,
    getSectionsForPart,
    getSubpartTOC,
    getSynonyms,
    getRegSearchResults,
    getSupplementalContentSearchGov,
    // API Export Insertion Point (do not change this text, it is being used by hygen cli)
};
