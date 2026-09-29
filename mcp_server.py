"""MCP JSON-RPC stdio server for genpark-proactive-intent-disambiguation-clarifier-skill."""
import sys
import json
from client import ProactiveIntentDisambiguationClarifier

clarifier = ProactiveIntentDisambiguationClarifier()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "disambiguate_intent":
        return {"error": f"Unknown tool '{name}'"}
        
    action = args.get("action")
    prompt = args.get("prompt", "")
    
    if action == "analyze_ambiguity":
        return clarifier.analyze_ambiguity(prompt)
    elif action == "generate_clarification":
        return clarifier.generate_clarification(prompt)
    elif action == "resolve_selection":
        return clarifier.resolve_selection(
            prompt=prompt,
            selection_index=args.get("selection_index", 1),
            custom_writein=args.get("custom_writein")
        )
    else:
        return {"error": f"Unknown action '{action}'"}

def main():
    if "--test" in sys.argv:
        print("[TEST] Running self-test for ProactiveIntentDisambiguationClarifier...")
        an = clarifier.analyze_ambiguity("clean up old database tables")
        assert an["needs_clarification"] is True
        cl = clarifier.generate_clarification("clean up old database tables")
        assert len(cl["options"]) >= 3
        res = clarifier.resolve_selection("clean up old database tables", 1)
        assert res["is_unambiguous"] is True
        print(f"[TEST] Success! Resolved plan: {res['executable_plan']}")
        return

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "disambiguate_intent",
                                "description": "Analyze user prompt ambiguity, assess execution risk, generate structured clarification options, and resolve intent.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["analyze_ambiguity", "generate_clarification", "resolve_selection"]},
                                        "prompt": {"type": "string"},
                                        "selection_index": {"type": "integer"},
                                        "custom_writein": {"type": "string"}
                                    },
                                    "required": ["action"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
