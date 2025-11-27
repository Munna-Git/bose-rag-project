"""
Format and structure LLM responses for better presentation
"""
from typing import Dict, List
from langchain_core.documents import Document
from src.error_handling.logger import logger


class ResponseFormatter:
    """Format responses with proper structure and citations"""
    
    def __init__(self):
        """Initialize response formatter"""
        self.template_format = "structured"
    
    def format_answer(self,
                      answer: str,
                      sources: List[Document],
                      query: str) -> Dict:
        """
        Format answer with sources and metadata
        
        Args:
            answer: Raw answer from LLM
            sources: Retrieved source documents
            query: Original query
        
        Returns:
            Formatted response dictionary
        """
        
        try:
            logger.debug("Formatting response...")
            
            # Clean answer
            clean_answer = self._clean_text(answer)
            
            # Format sources
            formatted_sources = self._format_sources(sources)
            
            # Build response
            response = {
                'query': query,
                'answer': clean_answer,
                'sources': formatted_sources,
                'source_count': len(sources),
                'has_sources': len(sources) > 0
            }
            
            logger.debug("Response formatted successfully")
            return response
        
        except Exception as e:
            logger.error(f"Response formatting failed: {str(e)}")
            return {
                'query': query,
                'answer': answer,
                'sources': [],
                'source_count': 0,
                'has_sources': False,
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Remove common artifacts
            text = text.replace('```', '')
            text = text.replace('Answer:', '').strip()
            text = text.replace('ANSWER:', '').strip()
            
            # Capitalize first letter if needed
            if text and text.islower():
                text = text.upper() + text[1:]
            
            return text
        
        except Exception as e:
            logger.warning(f"Text cleaning failed: {str(e)}")
            return text
    
    def _format_sources(self, sources: List[Document]) -> List[Dict]:
        """Format sources for display"""
        
        try:
            formatted_sources = []
            
            for idx, source in enumerate(sources, 1):
                metadata = source.metadata or {}
                
                source_info = {
                    'index': idx,
                    'page': metadata.get('page', 'Unknown'),
                    'content_type': metadata.get('content_type', 'TEXT'),
                    'source': metadata.get('source', 'Unknown'),
                    'snippet': self._get_snippet(source.page_content, 150)
                }
                
                formatted_sources.append(source_info)
            
            return formatted_sources
        
        except Exception as e:
            logger.error(f"Source formatting failed: {str(e)}")
            return []
    
    def _get_snippet(self, text: str, max_length: int = 150) -> str:
        """Get snippet from text"""
        
        try:
            if len(text) <= max_length:
                return text.strip()
            
            # Find good breaking point
            snippet = text[:max_length]
            last_period = snippet.rfind('.')
            last_space = snippet.rfind(' ')
            
            if last_period > max_length * 0.7:
                return text[:last_period + 1].strip()
            elif last_space > max_length * 0.7:
                return text[:last_space].strip() + "..."
            else:
                return snippet.strip() + "..."
        
        except Exception as e:
            logger.warning(f"Snippet extraction failed: {str(e)}")
            return text[:max_length].strip() + "..."
    
    def format_for_display(self, response: Dict) -> str:
        """Format response for console display"""
        
        try:
            output = []
            
            # Main answer
            output.append("=" * 70)
            output.append("ANSWER:")
            output.append("-" * 70)
            output.append(response['answer'])
            output.append("")
            
            # Sources
            if response['has_sources']:
                output.append("SOURCES:")
                output.append("-" * 70)
                
                for src in response['sources']:
                    output.append(f"{src['index']}. Page {src['page']} ({src['content_type']})")
                    output.append(f"   Source: {src['source']}")
                    output.append(f"   Snippet: {src['snippet']}")
                    output.append("")
            
            output.append("=" * 70)
            
            return "\n".join(output)
        
        except Exception as e:
            logger.error(f"Display formatting failed: {str(e)}")
            return response.get('answer', 'Error formatting response')
    
    def format_for_json(self, response: Dict) -> Dict:
        """Format response for JSON output"""
        
        try:
            return {
                'query': response['query'],
                'answer': response['answer'],
                'sources': response['sources'],
                'source_count': response['source_count'],
                'metadata': {
                    'has_sources': response['has_sources'],
                    'error': response.get('error')
                }
            }
        
        except Exception as e:
            logger.error(f"JSON formatting failed: {str(e)}")
            return {
                'query': response.get('query', ''),
                'answer': response.get('answer', ''),
                'error': str(e)
            }
