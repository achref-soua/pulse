from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os
from rag.retriever import chroma_retriever
from rag.query_router import QueryRouter
from dotenv import load_dotenv

load_dotenv()


class SurgicalAssistant:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",
            temperature=0.7,
        )
        self.query_router = QueryRouter()
        self.conversation_history = []

    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def retrieve_relevant_info(
        self, query: str, collections: List[str], patient_id: str = None
    ) -> str:
        """Retrieve relevant information from specified collections with patient filtering"""
        context = ""

        if patient_id:
            patient_info = chroma_retriever.get_patient_info(patient_id)
            if not patient_info:
                # Patient not found → hard stop
                return f"ERROR: Patient {patient_id} does not exist in the database. Please ask about an existing patient."
            context += (
                f"\n\n--- Patient Information ---\n{patient_info.json(indent=2)}\n"
            )

        for collection in collections:
            filters = (
                {"patient_id": patient_id}
                if (patient_id and collection == "notes")
                else None
            )
            results = chroma_retriever.query_collection(
                collection, query, filters=filters
            )
            if results:
                context += f"\n\n--- Information from {collection} ---\n"
                for i, result in enumerate(results[:3]):
                    if (
                        patient_id
                        and collection == "patients"
                        and result["metadata"].get("patient_id") == patient_id
                    ):
                        continue
                    context += f"\n{result['document']}\n"

        return context

    def get_system_prompt(self, phase: str, patient_id: str = None) -> str:
        """Get the appropriate system prompt based on phase"""
        base_prompt = ""

        if phase == "pre-op":
            base_prompt = """You are a specialized AI assistant for cardiac surgeons in the pre-operative phase. 
            Your role is to help with patient assessment, device selection, and surgical planning."""
        elif phase == "intra-op":
            base_prompt = """You are a specialized AI assistant for cardiac surgeons during surgery.
            Your role is to provide real-time guidance, device information, and procedural support."""
        elif phase == "post-op":
            base_prompt = """You are a specialized AI assistant for cardiac surgeons in the post-operative phase.
            Your role is to assist with recovery planning, monitoring, and follow-up care."""
        else:
            base_prompt = """You are a specialized AI assistant for cardiac surgeons.
            Provide helpful, evidence-based information to support surgical decision making."""

        # Add patient-specific instruction if applicable
        if patient_id:
            base_prompt += f"\n\nYou are currently assisting with patient {patient_id}. Focus your response specifically on this patient's case, using their medical information and history."

        base_prompt += """
        
        Always:
        1. Provide evidence-based recommendations
        2. Cite your sources from the available information
        3. Consider patient-specific factors when applicable
        4. Highlight any contraindications or risks
        5. Suggest alternatives when appropriate
        
        Be concise, professional, and focused on clinical decision support."""

        return base_prompt

    def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate a response to the query with routing information"""
        # Route the query to determine phase and collections
        routing_info = self.query_router.route_query(query)
        phase = routing_info.get("phase", "pre-op")
        collections = routing_info.get("collections", ["patients"])
        reasoning = routing_info.get("reasoning", "")
        patient_specific = routing_info.get("patient_specific", False)
        patient_id = routing_info.get("patient_id", None)

        # Retrieve relevant information
        context = self.retrieve_relevant_info(query, collections, patient_id)

        # Get appropriate system prompt
        system_prompt = self.get_system_prompt(phase, patient_id)

        # Prepare messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            *[
                HumanMessage(content=msg["content"])
                for msg in self.conversation_history[-6:]
                if msg["role"] == "user"
            ],
            *[
                SystemMessage(content=msg["content"])
                for msg in self.conversation_history[-6:]
                if msg["role"] == "assistant"
            ],
            HumanMessage(content=f"Context: {context}\n\nQuestion: {query}"),
        ]

        # Generate response
        response = self.llm.invoke(messages)

        # Update history
        self.add_to_history("user", query)
        self.add_to_history("assistant", response.content)

        if context.startswith("ERROR:"):
            return {
                "response": response.content,
                "phase": phase,
                "collections": collections,
                "patient_specific": patient_specific,
                "patient_id": patient_id,
                "reasoning": reasoning,
            }
