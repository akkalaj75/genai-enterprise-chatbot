"""
Evaluation metrics for RAG system performance
"""

from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class EvaluationMetrics:
    """Store and calculate RAG evaluation metrics"""
    
    def __init__(self):
        self.metrics = {
            'precision': [],
            'recall': [],
            'f1_score': [],
            'hallucination_rate': [],
            'latency': []
        }
    
    def calculate_precision(self, retrieved_docs: List[str], relevant_docs: List[str]) -> float:
        """
        Calculate precision: relevant docs / retrieved docs
        """
        if len(retrieved_docs) == 0:
            return 0.0
        relevant_count = len(set(retrieved_docs) & set(relevant_docs))
        precision = relevant_count / len(retrieved_docs)
        self.metrics['precision'].append(precision)
        return precision
    
    def calculate_recall(self, retrieved_docs: List[str], relevant_docs: List[str]) -> float:
        """
        Calculate recall: relevant docs / all relevant docs
        """
        if len(relevant_docs) == 0:
            return 0.0
        relevant_count = len(set(retrieved_docs) & set(relevant_docs))
        recall = relevant_count / len(relevant_docs)
        self.metrics['recall'].append(recall)
        return recall
    
    def calculate_f1(self, precision: float, recall: float) -> float:
        """Calculate F1 score"""
        if precision + recall == 0:
            return 0.0
        f1 = 2 * (precision * recall) / (precision + recall)
        self.metrics['f1_score'].append(f1)
        return f1
    
    def detect_hallucination(self, response: str, source_docs: List[str]) -> float:
        """
        Detect hallucination rate by checking if response is supported by source docs
        Returns hallucination_rate: 0 (no hallucination) to 1 (complete hallucination)
        """
        # Simple heuristic: check if key phrases from response appear in source
        words = set(response.lower().split())
        source_words = set()
        for doc in source_docs:
            source_words.update(doc.lower().split())
        
        supported_words = len(words & source_words)
        hallucination_rate = 1 - (supported_words / len(words)) if words else 0
        self.metrics['hallucination_rate'].append(hallucination_rate)
        return hallucination_rate
    
    def get_average_metrics(self) -> dict:
        """Get average of all recorded metrics"""
        averages = {}
        for metric_name, values in self.metrics.items():
            if values:
                averages[metric_name] = np.mean(values)
            else:
                averages[metric_name] = 0.0
        return averages
    
    def print_report(self):
        """Print evaluation report"""
        averages = self.get_average_metrics()
        print("\n" + "="*50)
        print("RAG EVALUATION REPORT")
        print("="*50)
        for metric, value in averages.items():
            print(f"{metric.upper()}: {value:.4f}")
        print("="*50 + "\n")

if __name__ == "__main__":
    # Example usage
    evaluator = EvaluationMetrics()
    
    # Simulate evaluation
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc4"]
    
    precision = evaluator.calculate_precision(retrieved, relevant)
    recall = evaluator.calculate_recall(retrieved, relevant)
    f1 = evaluator.calculate_f1(precision, recall)
    
    response = "Company provides health insurance"
    source_docs = ["Health insurance coverage starts on day 1", "Company pays 80% of premiums"]
    hallucination = evaluator.detect_hallucination(response, source_docs)
    
    evaluator.print_report()
