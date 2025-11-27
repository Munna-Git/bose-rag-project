#!/usr/bin/env python3
"""
Evaluation script for RAG system
Tests quality and performance
"""
import sys
import time
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger
from config.settings import config


class RAGEvaluator:
    """Evaluate RAG system performance and quality"""
    
    def __init__(self):
        """Initialize evaluator"""
        
        try:
            logger.info("Initializing RAG evaluator...")
            self.rag = BoseRAGPhi()
            self.results = {
                'total_queries': 0,
                'successful_queries': 0,
                'failed_queries': 0,
                'average_time': 0,
                'query_details': []
            }
            logger.info("✅ Evaluator initialized")
        
        except Exception as e:
            logger.error(f"Evaluator initialization failed: {str(e)}")
            raise
    
    def test_queries(self, queries: List[str]) -> Dict:
        """
        Test with sample queries
        
        Args:
            queries: List of test queries
        
        Returns:
            Evaluation results
        """
        
        logger.info(f"Starting evaluation with {len(queries)} queries...")
        
        times = []
        
        for i, query in enumerate(queries, 1):
            try:
                logger.info(f"Query {i}/{len(queries)}: {query}")
                
                # Time the query
                start = time.time()
                result = self.rag.answer_query(query, verbose=False)
                elapsed = time.time() - start
                
                times.append(elapsed)
                
                # Record result
                query_result = {
                    'query': query,
                    'status': result['status'],
                    'time': elapsed,
                    'answer_length': len(result.get('answer', '')),
                    'sources_count': len(result.get('sources', []))
                }
                
                self.results['query_details'].append(query_result)
                
                if result['status'] == 'success':
                    self.results['successful_queries'] += 1
                    logger.info(f"✅ Query {i} answered in {elapsed:.2f}s")
                else:
                    self.results['failed_queries'] += 1
                    logger.warning(f"⚠️ Query {i} failed")
            
            except Exception as e:
                logger.error(f"Query {i} failed with error: {str(e)}")
                self.results['failed_queries'] += 1
                self.results['query_details'].append({
                    'query': query,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Calculate statistics
        self.results['total_queries'] = len(queries)
        if times:
            self.results['average_time'] = sum(times) / len(times)
            self.results['min_time'] = min(times)
            self.results['max_time'] = max(times)
        
        return self.results
    
    def evaluate_performance(self) -> Dict:
        """Evaluate system performance"""
        
        logger.info("Evaluating system performance...")
        
        performance = {
            'memory_info': self._get_memory_info(),
            'model_info': self._get_model_info(),
            'system_health': self._get_system_health()
        }
        
        return performance
    
    def _get_memory_info(self) -> Dict:
        """Get memory information"""
        
        try:
            import psutil
            
            process = psutil.Process()
            mem_info = process.memory_info()
            
            return {
                'rss_mb': mem_info.rss / 1024 / 1024,
                'vms_mb': mem_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
        
        except ImportError:
            logger.warning("psutil not installed, skipping memory info")
            return {'error': 'psutil not installed'}
        
        except Exception as e:
            logger.error(f"Memory info failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_model_info(self) -> Dict:
        """Get model information"""
        
        try:
            info = self.rag.get_system_info()
            return info['model']
        
        except Exception as e:
            logger.error(f"Model info failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_system_health(self) -> Dict:
        """Get system health status"""
        
        try:
            info = self.rag.get_system_info()
            errors = info['errors']
            
            return {
                'documents_loaded': info['documents_loaded'],
                'total_errors': errors['total_errors'],
                'status': 'healthy' if errors['total_errors'] == 0 else 'degraded'
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {'error': str(e)}
    
    def generate_report(self) -> str:
        """Generate evaluation report"""
        
        logger.info("Generating evaluation report...")
        
        report = []
        report.append("\n" + "=" * 70)
        report.append("🔍 RAG SYSTEM EVALUATION REPORT")
        report.append("=" * 70)
        
        # Query Results
        report.append("\n📊 QUERY RESULTS:")
        report.append(f"  Total queries: {self.results['total_queries']}")
        report.append(f"  Successful: {self.results['successful_queries']}")
        report.append(f"  Failed: {self.results['failed_queries']}")
        report.append(f"  Success rate: {self._get_success_rate():.1f}%")
        
        # Performance
        report.append("\n⏱️  PERFORMANCE:")
        report.append(f"  Average time: {self.results.get('average_time', 0):.2f}s")
        report.append(f"  Min time: {self.results.get('min_time', 0):.2f}s")
        report.append(f"  Max time: {self.results.get('max_time', 0):.2f}s")
        
        # Details
        report.append("\n📝 QUERY DETAILS:")
        for i, detail in enumerate(self.results['query_details'], 1):
            report.append(f"  {i}. {detail['query'][:50]}...")
            report.append(f"     Status: {detail.get('status', 'unknown')}")
            report.append(f"     Time: {detail.get('time', 0):.2f}s")
            report.append(f"     Sources: {detail.get('sources_count', 0)}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def _get_success_rate(self) -> float:
        """Calculate success rate"""
        
        total = self.results['total_queries']
        if total == 0:
            return 0.0
        
        return (self.results['successful_queries'] / total) * 100
    
    def save_results(self, filepath: str = "evaluation_results.json"):
        """Save results to file"""
        
        try:
            results = {
                'summary': self.results,
                'performance': self.evaluate_performance()
            }
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return False


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG System Evaluator")
    parser.add_argument(
        '--queries',
        nargs='+',
        default=[
            "What is the SNR of DesignMax DM8SE?",
            "How do I configure ControlSpace?",
            "What is the frequency response range?",
            "What is the maximum SPL output?",
            "How to install the system?"
        ],
        help='Test queries'
    )
    parser.add_argument(
        '--output',
        default='evaluation_results.json',
        help='Output file for results'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator()
        
        # Run evaluation
        print("\n🚀 Starting RAG evaluation...\n")
        results = evaluator.test_queries(args.queries)
        
        # Print report
        report = evaluator.generate_report()
        print(report)
        
        # Save results
        evaluator.save_results(args.output)
        print(f"\n✅ Results saved to {args.output}\n")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        print("\n👋 Interrupted")
        return 0
    
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        print(f"\n❌ Evaluation failed: {str(e)}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
