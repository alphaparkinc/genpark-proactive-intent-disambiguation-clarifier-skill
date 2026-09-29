"""Example usage for ProactiveIntentDisambiguationClarifier."""
import json
from client import ProactiveIntentDisambiguationClarifier

def main():
    print("=== Proactive Intent Disambiguation Clarifier Demo ===")
    clarifier = ProactiveIntentDisambiguationClarifier()
    
    prompt = "purge old test user accounts"
    print(f"Testing Prompt: '{prompt}'")
    
    # 1. Analyze
    analysis = clarifier.analyze_ambiguity(prompt)
    print("Ambiguity Analysis:", json.dumps(analysis, indent=2))
    
    # 2. Clarification Options
    options = clarifier.generate_clarification(prompt)
    print("Clarification Question:", json.dumps(options, indent=2))
    
    # 3. Resolve Selection
    resolved = clarifier.resolve_selection(prompt, selection_index=1)
    print("Resolved Execution Directive:", json.dumps(resolved, indent=2))

if __name__ == "__main__":
    main()
