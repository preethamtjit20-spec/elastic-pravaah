"""HTTP client wrapping Elasticsearch and Kibana API calls."""

import json
import requests
from config import settings


class PravaahClient:
    """Unified client for Elasticsearch and Kibana APIs."""

    def __init__(self):
        settings.validate()
        self.es_url = settings.ES_URL
        self.kibana_url = settings.KIBANA_URL
        self.timeout = settings.REQUEST_TIMEOUT

    # -- Headers ----------------------------------------------------------

    def _es_headers(self):
        return {
            "Authorization": f"ApiKey {settings.ES_API_KEY}",
            "Content-Type": "application/json",
        }

    def _kibana_headers(self):
        return {
            "Authorization": f"ApiKey {settings.KIBANA_API_KEY}",
            "Content-Type": "application/json",
            "kbn-xsrf": "true",
            "elastic-api-version": "1",
        }

    # -- Elasticsearch helpers --------------------------------------------

    def es_request(self, method, path, body=None):
        url = f"{self.es_url}/{path.lstrip('/')}"
        resp = requests.request(
            method,
            url,
            headers=self._es_headers(),
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def create_index(self, name, body):
        """Create an index with given settings/mappings. Ignore if exists."""
        try:
            return self.es_request("PUT", f"/{name}", body)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400 and "already_exists" in e.response.text:
                return {"acknowledged": True, "note": "already exists"}
            raise

    def delete_index(self, name):
        """Delete an index. Ignore if not found."""
        try:
            return self.es_request("DELETE", f"/{name}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"acknowledged": True, "note": "not found"}
            raise

    def bulk_index(self, index, docs, pipeline=None, op_type="index"):
        """Bulk-index a list of dicts into the given index."""
        lines = []
        for doc in docs:
            meta = {op_type: {"_index": index}}
            lines.append(json.dumps(meta))
            lines.append(json.dumps(doc))
        body = "\n".join(lines) + "\n"

        url = f"{self.es_url}/_bulk"
        if pipeline:
            url += f"?pipeline={pipeline}"
        resp = requests.post(
            url,
            headers={
                "Authorization": f"ApiKey {settings.ES_API_KEY}",
                "Content-Type": "application/x-ndjson",
            },
            data=body,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("errors"):
            failed = [
                item.get(op_type, item.get("index", {})).get("error")
                for item in result["items"]
                if "error" in item.get(op_type, item.get("index", {}))
            ]
            if failed:
                raise RuntimeError(
                    f"Bulk indexing errors ({len(failed)}): {failed[:3]}"
                )
        return {
            "indexed": len(docs),
            "errors": result.get("errors", False),
        }

    def index_doc(self, index, doc, doc_id=None):
        """Index a single document."""
        path = f"/{index}/_doc"
        if doc_id:
            path += f"/{doc_id}"
        return self.es_request("POST" if not doc_id else "PUT", path, doc)

    def search(self, index, body):
        return self.es_request("POST", f"/{index}/_search", body)

    def esql_query(self, query, params=None):
        """Execute an ES|QL query."""
        body = {"query": query}
        if params:
            body["params"] = params
        return self.es_request("POST", "/_query", body)

    def put_index_template(self, name, body):
        """Create or update an index template."""
        return self.es_request("PUT", f"/_index_template/{name}", body)

    def create_data_stream(self, name):
        """Create a data stream."""
        return self.es_request("PUT", f"/_data_stream/{name}")

    def delete_data_stream(self, name):
        """Delete a data stream. Ignore if not found."""
        try:
            return self.es_request("DELETE", f"/_data_stream/{name}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"acknowledged": True, "note": "not found"}
            raise

    def delete_index_template(self, name):
        """Delete an index template. Ignore if not found."""
        try:
            return self.es_request("DELETE", f"/_index_template/{name}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"acknowledged": True, "note": "not found"}
            raise

    # -- Kibana helpers ---------------------------------------------------

    def kibana_request(self, method, path, body=None):
        url = f"{self.kibana_url}/{path.lstrip('/')}"
        resp = requests.request(
            method,
            url,
            headers=self._kibana_headers(),
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    # -- Agent Builder: Agents --------------------------------------------

    def create_agent(self, agent_def):
        """Register an agent via Kibana's Playground / Agent Builder API."""
        return self.kibana_request(
            "POST",
            "/internal/elastic_assistant/agents",
            agent_def,
        )

    def delete_agent(self, agent_id):
        try:
            return self.kibana_request(
                "DELETE",
                f"/internal/elastic_assistant/agents/{agent_id}",
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"deleted": False, "note": "not found"}
            raise

    def list_agents(self):
        return self.kibana_request("GET", "/internal/elastic_assistant/agents")

    # -- Agent Builder: Tools ---------------------------------------------

    def create_tool(self, tool_def):
        """Register a custom tool for Agent Builder."""
        return self.kibana_request(
            "POST",
            "/internal/elastic_assistant/tools",
            tool_def,
        )

    def delete_tool(self, tool_id):
        try:
            return self.kibana_request(
                "DELETE",
                f"/internal/elastic_assistant/tools/{tool_id}",
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"deleted": False, "note": "not found"}
            raise

    # -- Agent Builder: Workflows -----------------------------------------

    def create_workflow(self, workflow_def):
        return self.kibana_request(
            "POST",
            "/internal/elastic_assistant/workflows",
            workflow_def,
        )

    def delete_workflow(self, workflow_id):
        try:
            return self.kibana_request(
                "DELETE",
                f"/internal/elastic_assistant/workflows/{workflow_id}",
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"deleted": False, "note": "not found"}
            raise

    # -- Agent Builder: Converse (run agent) ------------------------------

    def converse(self, agent_id, message):
        """Send a message to an agent and get a response."""
        return self.kibana_request(
            "POST",
            f"/internal/elastic_assistant/agents/{agent_id}/converse",
            {"message": message},
        )
