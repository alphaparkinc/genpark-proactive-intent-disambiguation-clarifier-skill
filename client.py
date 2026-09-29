"""Client module for ProactiveIntentDisambiguationClarifier (100% Python Standard Library)."""
import json
import re
from typing import Dict, Any, List, Optional

class ProactiveIntentDisambiguationClarifier:
    """Detects under-specified parameters, evaluates irreversibility risk,
    and produces minimal multiple-choice clarification questions."""
    
    IRREVERSIBLE_KEYWORDS = {
        "delete": "irreversible_data_loss",
        "drop": "schema_drop",
        "purge": "permanent_purge",
        "send": "external_communication",
        "deploy": "production_modification",
        "charge": "financial_transaction",
        "publish": "public_broadcast"
    }

    def analyze_ambiguity(self, prompt: str) -> Dict[str, Any]:
        """Analyzes a user prompt for ambiguity, underspecification, and risk level."""
        prompt_lower = prompt.lower()
        detected_risks = []
        for kw, risk_type in self.IRREVERSIBLE_KEYWORDS.items():
            if re.search(r"" + kw + r"", prompt_lower):
                detected_risks.append({"keyword": kw, "risk_type": risk_type})
                
        # Ambiguity heuristics
        is_short = len(prompt.split()) < 5
        has_vague_terms = any(v in prompt_lower for v in ["clean up", "fix it", "make it better", "handle it", "update them", "remove everything"])
        has_missing_target = not any(v in prompt_lower for v in [".py", ".json", "http", "table", "user", "folder", "id"])
        
        ambiguity_score = 0.0
        if is_short: ambiguity_score += 0.35
        if has_vague_terms: ambiguity_score += 0.4
        if has_missing_target: ambiguity_score += 0.25
        
        ambiguity_score = min(1.0, ambiguity_score)
        needs_clarification = ambiguity_score >= 0.35 or len(detected_risks) > 0
        
        risk_tier = "low"
        if detected_risks:
            risk_tier = "high" if any(r["risk_type"] in ["irreversible_data_loss", "financial_transaction"] for r in detected_risks) else "medium"
            
        return {
            "status": "success",
            "prompt": prompt,
            "ambiguity_score": round(ambiguity_score, 2),
            "needs_clarification": needs_clarification,
            "risk_tier": risk_tier,
            "detected_risks": detected_risks
        }

    def generate_clarification(self, prompt: str) -> Dict[str, Any]:
        """Generates a structured multiple-choice clarification question."""
        analysis = self.analyze_ambiguity(prompt)
        prompt_lower = prompt.lower()
        
        if "delete" in prompt_lower or "clean" in prompt_lower or "remove" in prompt_lower:
            question = f"How would you like to handle the requested deletion/cleanup in '{prompt}'?"
            options = [
                {"id": 1, "text": "Dry-run only: Preview items that would be affected without deleting.", "recommended": True},
                {"id": 2, "text": "Soft delete / Archive: Move items to trash/archive with 30-day restore guarantee."},
                {"id": 3, "text": "Permanent hard delete: Delete matched records immediately."}
            ]
        elif "deploy" in prompt_lower or "publish" in prompt_lower or "send" in prompt_lower:
            question = f"Which environment or audience should this action target?"
            options = [
                {"id": 1, "text": "Staging / Draft mode: Verify in sandbox first.", "recommended": True},
                {"id": 2, "text": "Canary rollout: Deploy to 10% of users first."},
                {"id": 3, "text": "Immediate production rollout: Apply universally right away."}
            ]
        else:
            question = f"Could you clarify the primary objective for '{prompt}'?"
            options = [
                {"id": 1, "text": "Quick pass: Apply standard automated defaults.", "recommended": True},
                {"id": 2, "text": "Deep inspection: Run thorough end-to-end diagnostics and present report."},
                {"id": 3, "text": "Interactive step-by-step: Prompt me before executing each sub-action."}
            ]
            
        return {
            "status": "success",
            "prompt": prompt,
            "risk_tier": analysis["risk_tier"],
            "question": question,
            "options": options,
            "allows_custom_writein": True
        }

    def resolve_selection(self, prompt: str, selection_index: int, custom_writein: Optional[str] = None) -> Dict[str, Any]:
        """Resolves the user's clarification answer into a concrete, unambiguous execution specification."""
        clarification = self.generate_clarification(prompt)
        options = clarification["options"]
        
        if custom_writein:
            chosen_spec = f"User custom instruction: {custom_writein}"
        elif 1 <= selection_index <= len(options):
            chosen_spec = options[selection_index - 1]["text"]
        else:
            chosen_spec = options[0]["text"]  # Fallback to recommended default
            
        resolved_plan = f"Execute '{prompt}' according to directive: [{chosen_spec}]."
        return {
            "status": "success",
            "original_prompt": prompt,
            "resolved_directive": chosen_spec,
            "executable_plan": resolved_plan,
            "is_unambiguous": True
        }
