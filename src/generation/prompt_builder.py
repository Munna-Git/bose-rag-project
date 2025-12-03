"""
Prompt building for Phi-2 (optimized for local models)
"""
from typing import List
from langchain_core.documents import Document
from src.error_handling.logger import logger


class PromptBuilder:
    """Build prompts optimized for Phi-2 model"""
    
    def build_prompt(self,
                     query: str,
                     retrieved_docs: List[Document]) -> str:
        """
        Build prompt for Phi-2
        
        Phi-2 needs:
        - Simpler, clearer instructions
        - More structured format
        - Explicit context boundaries
        """
        
        try:
            # Analyze content types (keep all docs; no filtering)
            content_types = set(
                doc.metadata.get('content_type', 'TEXT')
                for doc in retrieved_docs
            )
            logger.debug(f"Building prompt with content types: {content_types}")
            
            # Build context - LIMIT TO TOP 2 DOCS AND TRUNCATE AGGRESSIVELY
            context_parts = []
            for i, doc in enumerate(retrieved_docs[:2], 1):  # Only use top 2 docs
                content_type = doc.metadata.get('content_type', 'TEXT')
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', '?')
                
                # Truncate to 200 chars per doc for speed
                content = doc.page_content[:200] if len(doc.page_content) > 200 else doc.page_content
                
                context_parts.append(
                    f"[Source {i}] {source} (Page {page})\n{content}"
                )
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Select prompt based on query intent
            if self._is_specification_query(query):
                prompt = self._spec_prompt(query, context)
            elif self._is_procedure_query(query):
                prompt = self._procedure_prompt(query, context)
            else:
                prompt = self._general_prompt(query, context)
            
            logger.debug("Prompt built successfully")
            return prompt
        
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            return self._fallback_prompt(query, retrieved_docs)

    
    
    def _is_specification_query(self, query: str) -> bool:
        """Detect specification queries"""
        keywords = [
            "specification", "spec", "what is the", "value",
            "rating", "db", "hz", "ohm", "maximum", "minimum",
            "frequency", "response", "snr", "spl",
            # Loudspeaker specs (DM6PE, DM8SE)
            "watt", "power", "impedance", "sensitivity", "driver",
            "coaxial", "two-way", "tweeter", "woofer", "pendant",
            "ceiling", "mounting", "coverage", "dispersion",
            # DSP/Processor specs (EX-1280)
            "channels", "input", "output", "i/o", "latency",
            "sample rate", "bit", "conversion", "processing",
            "dsp", "processor", "digital signal"
        ]
        return any(kw in query.lower() for kw in keywords)
    
    def _is_procedure_query(self, query: str) -> bool:
        """Detect procedure queries"""
        keywords = [
            "how", "configure", "setup", "install", "connect",
            "steps", "procedure", "guide", "set up", "connection",
            # Loudspeaker installation (DM6PE, DM8SE)
            "mount", "mounting", "wire", "wiring", "placement",
            "position", "angle", "height", "suspend", "attach",
            # DSP configuration (EX-1280)
            "program", "programming", "route", "routing", "assign",
            "configure", "configuration", "network", "ethernet",
            "firmware", "update", "reset", "initialize"
        ]
        return any(kw in query.lower() for kw in keywords)
    
    def _spec_prompt(self, query: str, context: str) -> str:
        """Prompt for specification queries"""
        return f"""You are a technical specification expert for Bose Professional Audio.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS: Answer in 1-2 sentences maximum. Be direct and technical. Include units. Use ONLY the documentation above. If the documentation does not contain this information, respond with: "I cannot find this specification in the available documentation."

ANSWER:"""
    
    def _procedure_prompt(self, query: str, context: str) -> str:
        """Prompt for procedure queries"""
        return f"""You are a technical support specialist for Bose Professional Audio.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS: Provide numbered steps using ONLY the documentation above. Maximum 5 steps. Be brief and clear. If the documentation does not contain this procedure, respond with: "I cannot find this procedure in the available documentation."

ANSWER:"""
    
    def _general_prompt(self, query: str, context: str) -> str:
        """Prompt for general queries"""
        return f"""You are an expert about Bose Professional Audio products.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS: 
1. Answer ONLY questions about Bose audio equipment using the documentation above
2. If the question is not about Bose audio products, respond: "I can only assist with Bose Professional Audio equipment."
3. Answer in 2-3 sentences maximum. Be direct and accurate.
4. If the documentation does not contain enough information, respond: "I cannot find sufficient information about this in the available documentation."

ANSWER:"""
    
    def _fallback_prompt(self, query: str, docs: List[Document]) -> str:
        """Fallback prompt if building fails"""
        context = "\n".join([doc.page_content[:200] for doc in docs])
        return f"""Based on the following information, answer: {query}\n\n{context}\n\nAnswer:"""
