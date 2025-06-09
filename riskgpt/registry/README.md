# Chain Registry

## Overview

The Chain Registry provides a lightweight, framework-agnostic system for registering, retrieving, and introspecting chains (callable functions) by name. It's designed to be easily integrated with any web framework or service without adding dependencies.

## Key Features

- **Register chains** with simple decorators
- **Retrieve chains** by name for dynamic invocation
- **Introspect available chains** with metadata
- **No server dependencies** - works with any framework

## Usage with External Servers

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from riskgpt.registry import chain_registry

app = FastAPI()

# List all available chains
@app.get("/chains")
def list_chains():
    return {"chains": chain_registry.get_chain_info()}

# Get details about a specific chain
@app.get("/chains/{chain_name}")
def get_chain_details(chain_name: str):
    signature = chain_registry.get_chain_signature(chain_name)
    if not signature:
        raise HTTPException(status_code=404, detail=f"Chain '{chain_name}' not found")
    return signature

# Execute a chain
@app.post("/chains/{chain_name}")
def execute_chain(chain_name: str, data: dict):
    if not chain_registry.chain_exists(chain_name):
        raise HTTPException(status_code=404, detail=f"Chain '{chain_name}' not found")
    try:
        chain_func = chain_registry.get(chain_name)
        return chain_func(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Flask Example

```python
from flask import Flask, jsonify, request
from riskgpt.registry import chain_registry

app = Flask(__name__)

@app.route('/chains', methods=['GET'])
def list_chains():
    return jsonify({"chains": chain_registry.get_chain_info()})

@app.route('/chains/<chain_name>', methods=['GET'])
def get_chain_details(chain_name):
    signature = chain_registry.get_chain_signature(chain_name)
    if not signature:
        return jsonify({"error": f"Chain '{chain_name}' not found"}), 404
    return jsonify(signature)

@app.route('/chains/<chain_name>', methods=['POST'])
def execute_chain(chain_name):
    if not chain_registry.chain_exists(chain_name):
        return jsonify({"error": f"Chain '{chain_name}' not found"}), 404
    try:
        data = request.get_json()
        chain_func = chain_registry.get(chain_name)
        return jsonify(chain_func(**data))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

## Best Practices

1. **Type Annotations**: Add proper type hints to your chain functions for better introspection
2. **Docstrings**: Include clear documentation in your chain functions
3. **Error Handling**: Wrap chain execution in try/except blocks in your server code
4. **Validation**: Consider adding input validation in your server integration

Remember that the registry itself remains framework-agnostic - it simply provides the tooling for your chosen framework to integrate with.
