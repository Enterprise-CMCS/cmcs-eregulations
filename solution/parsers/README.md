# Parser Lambdas

This directory contains the parser services:

- `ecfr-launcher` and `ecfr-worker`
- `fr-launcher` and `fr-worker`
- `common` shared auth/config/http helpers
- `tests` unit tests for both pipelines

## How the parsers work

Both parser families follow the same split architecture:

- launcher discovers work and creates one work unit per item
- worker consumes exactly one work unit and uploads results to eRegs

Pipelines:

- eCFR: config + title/part discovery -> queue one unit per part -> parse XML/structure -> upload part and locations
- FR: config + Federal Register discovery -> queue one unit per document -> extract section links -> upload Federal Register doc

In local mode (`PARSER_LOCAL_MODE=true`), launchers call workers over HTTP through lambda-proxy. In deployed mode, launchers send to SQS.

## Parser flowcharts

The diagrams below show the deployed flow. In local mode, the launcher-to-SQS edge is replaced by a POST through lambda-proxy to the worker; the worker pipeline is otherwise the same.

<details>
<summary>eCFR launcher flowchart</summary>


```mermaid
flowchart TD
    ecfrSchedule["EventBridge daily schedule<br/>or manual invoke"] --> ecfrLauncher["eCFR launcher"]
    ecfrLauncher --> ecfrCredentials["Resolve eRegs credentials<br/>from runtime configuration"]
    ecfrCredentials --> ecfrConfig["GET /v3/parsers/config"]
    ecfrConfig --> ecfrRun["POST /v3/parsers/ecfr/launcher-results<br/>create launcher-run record"]
    ecfrRun --> ecfrTargets["Expand configured part and<br/>subchapter targets"]
    ecfrTargets --> ecfrVersions["GET eCFR versions per title<br/>paginate all response pages"]
    ecfrVersions --> ecfrSkipSetting{"skip_parsed_regs?"}
    ecfrSkipSetting -- "yes" --> ecfrProcessed["GET /v3/parsers/ecfr/results/title/{title}/processed-dates"]
    ecfrSkipSetting -- "no" --> ecfrCompare["Compare each target with<br/>latest eCFR issue_date"]
    ecfrProcessed --> ecfrCompare
    ecfrCompare --> ecfrStatus{"Latest date missing<br/>or already processed?"}
    ecfrStatus -- "yes" --> ecfrSkipped["POST eCFR parser result<br/>status=skipped"]
    ecfrStatus -- "no" --> ecfrQueued["POST eCFR parser result<br/>status=queued"]
    ecfrQueued --> ecfrWorkUnit["Build one work unit per part<br/>including parser_result_id"]
    ecfrSkipped --> ecfrTargetsReady["All target statuses recorded"]
    ecfrWorkUnit --> ecfrTargetsReady
    ecfrTargetsReady --> ecfrDispatch
    ecfrDispatch -- "deployed" --> ecfrQueue["SQS ecfr-parser-queue<br/>one message per queued part"]
    ecfrDispatch -- "local" --> ecfrWorkerHttp["POST through lambda-proxy<br/>to eCFR worker"]
    ecfrQueue --> ecfrUpdate["PATCH latest eCFR launcher result<br/>with queued/skipped outcome"]
    ecfrWorkerHttp --> ecfrUpdate
    ecfrUpdate --> ecfrResponse["Return launcher response"]
    ecfrTargets -. "target processing or discovery error" .-> ecfrFailure["Record failed launcher result<br/>and re-raise"]
    ecfrDispatch -. "dispatch error" .-> ecfrFailure
```

The launcher creates the run record before processing targets. Each target gets its own `EcfrParserResult`: skipped targets are terminal immediately, while queued targets carry the result ID that the worker later updates.

</details>

<details>
<summary>eCFR worker flowchart</summary>


```mermaid
flowchart TD
    ecfrQueue["SQS ecfr-parser-queue<br/>or local lambda-proxy POST"] --> ecfrSingle["Require exactly one work unit"]
    ecfrSingle --> ecfrParse["Parse and validate part config"]
    ecfrParse --> ecfrStructure["GET eCFR current structure<br/>for title and part"]
    ecfrStructure --> ecfrNormalize["Normalize structure<br/>and determine depth"]
    ecfrNormalize --> ecfrText{"upload_reg_text?"}
    ecfrText -- "yes" --> ecfrXml["GET eCFR full XML<br/>for effective_date"]
    ecfrXml --> ecfrXmlParse["Parse XML into normalized<br/>regulation document"]
    ecfrText -- "no" --> ecfrLocations{"upload_locations?"}
    ecfrXmlParse --> ecfrLocations
    ecfrLocations -- "yes" --> ecfrExtract["Extract sections and subparts<br/>from normalized structure"]
    ecfrLocations -- "no" --> ecfrPayload["Build part upload payload"]
    ecfrExtract --> ecfrPayload
    ecfrPayload --> ecfrUpload["PUT /v3/parsers/ecfr/parts<br/>current Part data, text, structure,<br/>and optional locations"]
    ecfrUpload --> ecfrSuccess["PATCH /v3/parsers/ecfr/results/{id}<br/>status=succeeded"]
    ecfrSuccess --> ecfrDone["Return success"]
    ecfrParse -. "parse, upstream, or upload error" .-> ecfrError["PATCH result status=failed"]
    ecfrStructure -. "error" .-> ecfrError
    ecfrXml -. "error" .-> ecfrError
    ecfrUpload -. "error" .-> ecfrError
    ecfrError --> ecfrRetry["Re-raise error for SQS redelivery"]
    ecfrRetry --> ecfrDlq["After retry policy: ecfr-parser-dlq"]
```

The eCFR upload endpoint is also the integration point for saving current regulation data and triggering downstream regulation-text indexing when configured. The parser result row is the per-part status source of truth for last-updated behavior.

</details>

<details>
<summary>Federal Register launcher flowchart</summary>


```mermaid
flowchart TD
    frSchedule["EventBridge daily schedule<br/>or manual invoke"] --> frLauncher["FR launcher"]
    frLauncher --> frCredentials["Resolve eRegs credentials<br/>from runtime configuration"]
    frCredentials --> frConfig["GET /v3/parsers/config"]
    frConfig --> frTargets["Expand upload_fr_docs part<br/>and subchapter targets"]
    frTargets --> frSkipSetting{"skip_fr_documents?"}
    frSkipSetting -- "yes" --> frExisting["GET /v3/resources/public/<br/>federal_register_links/document_numbers"]
    frSkipSetting -- "no" --> frDiscover["Discover documents per target"]
    frExisting --> frDiscover
    frDiscover --> frApi["Paginate Federal Register API<br/>for each title and part"]
    frApi --> frDedupe["Remove document_numbers<br/>already stored in eRegs"]
    frDedupe --> frWorkUnits["Build one work unit per document<br/>after optional dedupe"]
    frWorkUnits --> frDispatch{"PARSER_LOCAL_MODE?"}
    frDispatch -- "deployed" --> frQueue["SQS fr-parser-queue<br/>one message per document"]
    frDispatch -- "local" --> frWorkerHttp["POST through lambda-proxy<br/>to FR worker"]
    frQueue --> frRun["POST /v3/parsers/fr/launcher-results<br/>counts and run outcome"]
    frWorkerHttp --> frRun
    frRun --> frResponse["Return launcher response"]
    frTargets -. "target processing or discovery error" .-> frFailure["Record failed launcher result<br/>and re-raise"]
    frDispatch -. "dispatch error" .-> frFailure
```

The FR launcher records its counts-only launcher result after dispatching work. Unlike eCFR, it does not pre-create one parser-result row per document.

</details>

<details>
<summary>Federal Register worker flowchart</summary>


```mermaid
flowchart TD
    frQueue["SQS fr-parser-queue<br/>or local lambda-proxy POST"] --> frSingle["Require exactly one document"]
    frSingle --> frParse["Parse and validate document config"]
    frParse --> frXmlAvailable{"full_text_xml_url present?"}
    frXmlAvailable -- "no" --> frNoLinks["Continue with no section links"]
    frXmlAvailable -- "yes" --> frFetchXml["GET Federal Register full-text XML"]
    frFetchXml --> frExtract["Extract SECTNO/CFR references"]
    frExtract --> frBuildLinks["Build section and section-range<br/>link payloads"]
    frFetchXml -. "fetch or XML error" .-> frExtractFallback["Log error and continue<br/>without section links"]
    frExtract -. "extraction error" .-> frExtractFallback
    frNoLinks --> frUpload
    frBuildLinks --> frUpload["PUT /v3/resources/public/<br/>federal_register_links<br/>upsert by document_number"]
    frExtractFallback --> frUpload
    frUpload --> frResult["POST /v3/parsers/fr/results<br/>success result for document"]
    frResult --> frDone["Return success"]
    frParse -. "validation or fatal error" .-> frFailureResult["POST FR parser result<br/>success=false with log"]
    frUpload -. "upload error" .-> frFailureResult
    frResult -. "result-post error" .-> frFailureResult
    frFailureResult --> frRetry["Re-raise error for SQS redelivery"]
    frRetry --> frDlq["After retry policy: fr-parser-dlq"]
```

FR section-link extraction is intentionally non-fatal: missing XML or an extraction failure still allows the Federal Register document itself to be upserted. A document upload failure remains fatal so SQS can retry it.

</details>

### eRegs data destinations

| Parser stage | eRegs destination | Purpose |
| --- | --- | --- |
| eCFR launcher | `/v3/parsers/ecfr/launcher-results` | Records each launcher invocation and its outcome. |
| eCFR launcher/worker | `/v3/parsers/ecfr/results` | Records one per-part status row; the worker updates queued rows to succeeded or failed. |
| eCFR worker | `/v3/parsers/ecfr/parts` | Upserts current Part data, regulation text, structure, depth, sections, and subparts according to upload flags. |
| FR launcher | `/v3/parsers/fr/launcher-results` | Records document counts and launcher outcome. |
| FR worker | `/v3/resources/public/federal_register_links` | Upserts Federal Register metadata and extracted section/range links by document number. |
| FR worker | `/v3/parsers/fr/results` | Records one success or failure result per processed document. |

### eCFR flow details

- `ecfr-launcher/app.py` is the entry point and orchestration layer.
- `ecfr-launcher/eregs_config.py` expands parser config targets (`part` + `subchapter`) into concrete title/part work.
- `ecfr-launcher/ecfr_versions.py` resolves the latest `issue_date` per part before queueing.
- `ecfr-worker/app.py` executes one part ingest pipeline per message.
- `ecfr-worker/transforms/` shapes structure payloads and extracts section/subpart location data.
- `ecfr-worker/xml_parser/` parses full eCFR XML into normalized document payloads.

### FR flow details

- `fr-launcher/app.py` orchestrates config fetch, document discovery, dedupe, and dispatch.
- `fr-launcher/fedreg_client.py` handles Federal Register API pagination and document extraction.
- `fr-launcher/frlaunch_config.py` expands `upload_fr_docs` part/subchapter targets.
- `fr-worker/app.py` processes one document at a time, uploads the Federal Register link, then posts a parser result.
- `fr-worker/fedreg_client.py` extracts SECTNO/CFR references from full-text XML.
- `fr-worker/links.py` builds section + section-range payloads for eRegs serializers.

## Directory map

- `ecfr-launcher/`: eCFR discovery and work-unit creation
- `ecfr-worker/`: eCFR parsing + upload pipeline
- `fr-launcher/`: Federal Register discovery, dedupe, and queueing
- `fr-worker/`: Federal Register document processing + upload
- `common/`: shared auth, config, logging, HTTP, queue dispatch
- `tests/`: parser unit tests (run with `make parsers.test`)

Shared modules in `common/` are intentionally thin and reusable:

- `auth.py`: credentials resolution + auth header construction
- `config.py`: strict config/event parsing helpers
- `eregs_client.py`: shared authenticated JSON request helper for parser -> eRegs calls
- `http.py`: request execution + JSON-shape validation wrappers
- `launcher.py`: local-vs-queue dispatch helpers and API-Gateway-style response builder
- `logging.py`: parser log-level normalization and runtime logger configuration
- `ecfr.py` and `fedreg.py`: shared parser-domain helpers and exceptions

## Local development workflow

From `solution/`:

```bash
make parsers.local.build
make parsers.local.up
```

Common commands:

```bash
make parsers.local.invoke.ecfr-launcher
make parsers.local.invoke.fr-launcher
make parsers.local.logs
make parsers.local.down
make parsers.test
```

Local proxy endpoints:

- `ecfr-worker`: `http://localhost:8003`
- `fr-worker`: `http://localhost:8004`
- `ecfr-launcher`: `http://localhost:8005`
- `fr-launcher`: `http://localhost:8006`

Tip: rebuild (`make parsers.local.build`) whenever Dockerfiles, dependencies, or `common/` code changes.

If you are iterating on only Python source (no Dockerfile/dependency changes), `make parsers.local.up` after edits is usually enough because compose bind-mounts parser source directories.

## Key behavior notes

- Workers accept either SQS-style events or lambda-proxy HTTP events.
- Worker credentials are runtime-resolved only: `EREGS_AUTH_SECRET_NAME` -> `EREGS_BEARER_TOKEN` -> `EREGS_USERNAME`/`EREGS_PASSWORD`.
- Launchers resolve log level from parser config and include it in worker work units.
- FR dedupe is controlled by parser config (`skip_fr_documents`) using existing `document_number` values in eRegs.
- FR section-link extraction is non-fatal: a document still uploads even if link extraction fails.

Additional contracts to keep in mind:

- eCFR worker status rows are part-level and transition monotonically toward success (`queued/failed -> succeeded` allowed; terminal statuses are not downgraded).
- FR worker upserts Federal Register documents by `document_number` through the resources endpoint.
- Parser result APIs under `/v3/parsers/` are part of the runtime contract for launcher/worker observability.

## Practical debugging tips

- If local launcher runs enqueue `0/N`, check `PARSER_LOCAL_MODE`, `PARSER_WORKER_URL`, and worker logs first.
- If eCFR launcher skips too much (or nothing), inspect `/v3/parsers/config` and `/v3/parsers/ecfr/results/title/<title>/processed-dates` responses.
- If FR uploads succeed but results fail, check `/v3/parsers/fr/results` validation errors in backend logs.

Quick places to start when debugging code:

- Launcher orchestration bugs: `ecfr-launcher/app.py` or `fr-launcher/app.py`
- Config expansion issues: `ecfr-launcher/eregs_config.py` or `fr-launcher/frlaunch_config.py`
- Worker upload payload issues: `ecfr-worker/eregs_client.py` or `fr-worker/eregs_client.py`
- Shared transport/auth behavior: `common/http.py`, `common/eregs_client.py`, `common/auth.py`

## Manual invoke (optional)

Most development should use `make parsers.local.invoke.*`. Manual invoke is useful for targeted debugging:

```bash
curl -s -X POST http://localhost:8005 -H 'Content-Type: application/json' -d '{}'
curl -s -X POST http://localhost:8006 -H 'Content-Type: application/json' -d '{}'
```

To invoke workers directly, POST a JSON body with a `config` object matching each worker's expected payload schema. Use this sparingly; launcher-driven invocation better matches production behavior.
