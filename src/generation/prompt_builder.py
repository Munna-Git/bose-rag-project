"""
Prompt building for Phi-2 (optimized for local models)
"""
from typing import List
from langchain.schema import Document
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
            # Analyze content types
            content_types = set(
                doc.metadata.get('content_type', 'TEXT')
                for doc in retrieved_docs
            )
            
            logger.debug(f"Building prompt with content types: {content_types}")
            
            # Build context
            context_parts = []
            for i, doc in enumerate(retrieved_docs, 1):
                content_type = doc.metadata.get('content_type', 'TEXT')
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', '?')
                
                context_parts.append(
                    f"[Source {i}] {source} (Page {page}, Type: {content_type})\n"
                    f"{doc.page_content}"
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
            "frequency", "response", "snr", "spl"
        ]
        return any(kw in query.lower() for kw in keywords)
    
    def _is_procedure_query(self, query: str) -> bool:
        """Detect procedure queries"""
        keywords = [
            "how", "configure", "setup", "install", "connect",
            "steps", "procedure", "guide", "set up", "connection"
        ]
        return any(kw in query.lower() for kw in keywords)
    
    def _spec_prompt(self, query: str, context: str) -> str:
        """Prompt for specification queries"""
        return f"""You are a technical specification expert for Bose Professional Audio.

Use ONLY the provided documentation to answer the question.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Answer using ONLY the documentation above
2. Be specific and technical
3. Include units (dB, Hz, Ohm) when applicable
4. If not found, say "Not mentioned in the provided documents"
5. Be concise

ANSWER:"""
    
    def _procedure_prompt(self, query: str, context: str) -> str:
        """Prompt for procedure queries"""
        return f"""You are a technical support specialist for Bose Professional Audio.

Use ONLY the provided documentation for step-by-step instructions.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Use numbered steps (1, 2, 3, etc.)
2. Use ONLY the documentation
3. Be clear and practical
4. If not documented, say "Instructions not found in documentation"
5. Keep it brief

ANSWER:"""
    
    def _general_prompt(self, query: str, context: str) -> str:
        """Prompt for general queries"""
        return f"""You are an expert about Bose Professional Audio products.

Answer using ONLY the provided documentation.

DOCUMENTATION:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Use only the documentation above
2. Be accurate and helpful
3. Say if information is not available
4. Keep response brief

ANSWER:"""
    
    def _fallback_prompt(self, query: str, docs: List[Document]) -> str:
        """Fallback prompt if building fails"""
        context = "\n".join([doc.page_content[:200] for doc in docs])
        return f"""Based on the following information, answer: {query}\n\n{context}\n\nAnswer:"""
