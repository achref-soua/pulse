from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
import json
import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
import pickle
import yaml

load_dotenv()


# Structured model for routing outputs
class RoutingDecision(BaseModel):
    phase: str = Field(..., pattern="^(pre-op|intra-op|post-op)$")
    collections: list[str]
    patient_specific: bool
    reasoning: str
    patient_id: str | None = None


class QueryRouter:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",
            temperature=0.1,
        )

        # Load config.yaml
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Load phase classifier if available
        clf_path = os.path.join(
            os.path.dirname(__file__), "..", "database", "phase_classifier.pkl"
        )
        if os.path.exists(clf_path):
            with open(clf_path, "rb") as f:
                self.vectorizer, self.phase_clf = pickle.load(f)
        else:
            self.vectorizer, self.phase_clf = None, None

    def extract_patient_id(self, query: str) -> str | None:
        """Extract patient ID from query if mentioned"""
        patient_patterns = [
            r"patient\s+([Pp]\d{3})",
            r"([Pp]\d{3})",
            r"pt\s+([Pp]\d{3})",
            r"case\s+([Pp]\d{3})",
        ]
        for pattern in patient_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def classify_phase(self, query: str) -> str:
        """Use ML classifier if available, else fallback regex"""
        if self.phase_clf and self.vectorizer:
            X = self.vectorizer.transform([query])
            return self.phase_clf.predict(X)[0]
        return self._fallback_phase(query)

    def route_query(self, query: str) -> Dict[str, Any]:
        patient_id = self.extract_patient_id(query)
        phase = self.classify_phase(query)

        # Get default collections from config.yaml for this phase
        default_collections = self.config.get("collections", {}).get(phase, [])

        prompt = ChatPromptTemplate.from_template("""
        You are a medical AI assistant specializing in cardiac surgery. 
        Determine which knowledge collections are most relevant for this query.
        
        Available collections:
        - patients
        - devices
        - guidelines
        - literature
        - notes

        Query: {query}

        Respond strictly in JSON:
        {{
            "collections": ["collection1", "collection2"],
            "reasoning": "Why these collections are relevant"
        }}
        """)

        chain = prompt | self.llm
        response = chain.invoke({"query": query})

        try:
            # Parse JSON safely
            json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
            parsed = json.loads(json_match.group()) if json_match else {}

            # Use LLM-provided collections if valid, else fall back to config.yaml defaults
            collections = (
                parsed.get("collections", []) or default_collections or ["patients"]
            )

            routing = RoutingDecision(
                phase=phase,
                collections=collections,
                patient_specific=bool(patient_id),
                reasoning=parsed.get("reasoning", "")
                + (f" Query mentions {patient_id}" if patient_id else ""),
                patient_id=patient_id,
            )
            return routing.dict()

        except (json.JSONDecodeError, ValidationError):
            # Delegate to fallback routing to avoid duplication
            return self._fallback_routing(query, patient_id)

    def _fallback_phase(self, query: str) -> str:
        q = query.lower()
        if any(term in q for term in ["intra-op", "surgery", "deployment", "during"]):
            return "intra-op"
        if any(term in q for term in ["post-op", "recovery", "follow-up"]):
            return "post-op"
        return "pre-op"

    def _fallback_routing(self, query: str, patient_id: str | None):
        phase = self._fallback_phase(query)
        default_collections = self.config.get("collections", {}).get(
            phase, ["patients"]
        )
        return {
            "phase": phase,
            "collections": default_collections,
            "patient_specific": bool(patient_id),
            "reasoning": "Fallback routing used.",
            "patient_id": patient_id,
        }
