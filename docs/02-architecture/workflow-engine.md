# Node-Based DAG Workflow Engine

VidGen implements a Directed Acyclic Graph (DAG) **Workflow Engine** (`WorkflowExecutor`) that decouples model definitions from static code routines.

---

## 🤖 Workflow Architecture

Each AI model in `generation_models` references a JSON-encoded node graph in the `workflows` table.

```
+-------------------+      +-------------------+      +-----------------------+
|  User Input Node  | ---> | Parameter Mapping | ---> |   API Call Node       |
|  (Prompt, Image)  |      | Preset Guidance   |      |   (Replicate / Flux)  |
+-------------------+      +-------------------+      +-----------+-----------+
                                                                  |
                                                                  v
                                                      +-----------------------+
                                                      |   Output Asset Node   |
                                                      | (Cloudflare R2 / S3)  |
                                                      +-----------------------+
```

---

## 📄 Node Graph JSON Protocol

The workflow graph consists of `nodes` and `edges`:

```json
[
  {
    "id": "node_api_1",
    "type": "api_call",
    "api_id": "replicate_flux_1_dev",
    "data": {
      "preset_params": {
        "num_inference_steps": 25,
        "guidance_scale": 7.5
      },
      "param_mappings": {
        "prompt": "$.user_input.prompt",
        "aspect_ratio": "$.user_input.aspect_ratio"
      }
    }
  }
]
```

---

## ⚡ Execution Pipeline

1. **Graph Resolution**: `WorkflowExecutor` topologically sorts nodes and evaluates JSONPath mapping expressions (`$.user_input.prompt`).
2. **Provider Invocation**: Adapter executes the external AI API call.
3. **Asset Persistence**: Media output stream is automatically fetched and saved to Cloudflare R2 / S3 storage.
4. **WebSocket Notification**: Broadcasts progress and output CDN URL to the user client.
