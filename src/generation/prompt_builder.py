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
            # Intent & keyword filtering to keep only relevant context
            intent = (
                'spec' if self._is_specification_query(query)
                else 'proc' if self._is_procedure_query(query)
                else 'general'
            )

            keywords = self._intent_keywords(query, intent)
            filtered = []
            for doc in retrieved_docs:
                text_low = doc.page_content.lower()
                meta_low = ' '.join(str(v).lower() for v in (doc.metadata or {}).values())
                if any(k in text_low or k in meta_low for k in keywords):
                    filtered.append(doc)

            # If filtering removed everything, fall back to the original docs
            docs_for_prompt = filtered if filtered else retrieved_docs[:5]
            logger.debug(
                f"Prompt intent={intent} keywords={keywords} | using {len(docs_for_prompt)} of {len(retrieved_docs)} docs"
            )
            
            # Build context
            context_parts = []
            for i, doc in enumerate(docs_for_prompt, 1):
                content_type = doc.metadata.get('content_type', 'TEXT')
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', '?')
                
                context_parts.append(
                    f"[Source {i}] {source} (Page {page}, Type: {content_type})\n"
                    f"{doc.page_content}"
                )
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Select prompt based on query intent
            if intent == 'spec':
                prompt = self._spec_prompt(query, context)
            elif intent == 'proc':
                prompt = self._procedure_prompt(query, context)
            else:
                prompt = self._general_prompt(query, context)
            
            logger.debug("Prompt built successfully")
            return prompt
        
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            return self._fallback_prompt(query, retrieved_docs)

    def _intent_keywords(self, query: str, intent: str) -> List[str]:
        """Keywords used to filter context based on intent and query."""
        q = query.lower()
        base = []
        # Extract possible product references from query
        for token in [
            'ex-1280c', 'ex1280c', 'controlspace', 'designmax', 'dm8se',
            'analog', 'inputs', 'input', 'channels', 'euroblock'
        ]:
            if token in q:
                base.append(token)

        if intent == 'spec':
            spec_terms = [
                'analog inputs', 'input channels', 'mic/line', 'mic input',
                'line input', 'balanced', 'euroblock', 'specifications',
                'maximum', 'max', 'qty', 'count', 'inputs'
            ]
            return list(set(base + spec_terms))
        elif intent == 'proc':
            proc_terms = ['configure', 'setup', 'install', 'connection', 'steps', 'procedure']
            return list(set(base + proc_terms))
        else:
            return list(set(base + ['specifications', 'features']))
    
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
        return f"""You are a technical specification assistant.

    Use ONLY the provided documentation to answer. Do not invent, roleplay, or infer beyond the text.

    DOCUMENTATION:
    {context}

    QUESTION: {query}

    ANSWER FORMAT:
    - First line: the exact value if present (e.g., "12 analog inputs")
    - Second line: brief justification quoting the source (page and snippet)
    - If not present: write "Not mentioned in the provided documents"

    STRICT RULES:
    1) Use ONLY the documentation above
    2) Prefer exact counts and units from tables/specs
    3) Do NOT discuss unrelated outputs (e.g., outputs vs inputs)
    4) Keep total under 3 lines

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
