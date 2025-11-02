#!/usr/bin/env python3
# golden-validate.py
# Validates RAG retrieval accuracy against golden dataset
# Returns non-zero exit code if pass rate below threshold (CI-friendly)

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

def load_golden_dataset(path: Path) -> Dict:
    """Load and validate golden dataset JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'tests' not in data:
        raise ValueError("Golden dataset missing 'tests' key")
    
    return data

def query_rag_endpoint(
    api_base: str,
    query: str,
    standard: Optional[str] = None,
    top_k: int = 5,
    timeout: int = 15
) -> Dict:
    """
    Query the RAG compliance endpoint
    
    Returns:
        Dict with 'answer', 'citations', 'metadata', 'latency_ms'
    """
    url = f"{api_base}/v1/chat/compliance"
    payload = {
        "query": query,
        "top_k": top_k
    }
    if standard:
        payload["standard"] = standard
    
    start_time = time.time()
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        latency_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            data['latency_ms'] = latency_ms
            return data
        else:
            return {
                'error': f"HTTP {response.status_code}",
                'detail': response.text,
                'latency_ms': latency_ms
            }
    except requests.exceptions.Timeout:
        return {
            'error': 'timeout',
            'detail': f'Request exceeded {timeout}s timeout',
            'latency_ms': timeout * 1000
        }
    except Exception as e:
        return {
            'error': 'exception',
            'detail': str(e),
            'latency_ms': (time.time() - start_time) * 1000
        }

def normalize_clause_id(clause_id: str) -> str:
    """
    Normalize clause IDs for flexible matching
    
    Examples:
      "aws_d1.1_2020_4.2.3" -> "4.2.3"
      "Table 4.1" -> "4.1"  (extract numeric part)
      "4.2.3" -> "4.2.3"
    """
    # Remove standard prefix if present
    if 'aws' in clause_id.lower():
        parts = clause_id.split('_')
        if len(parts) >= 4:
            clause_id = '_'.join(parts[3:])
    
    # Handle "Table X.Y" format
    if clause_id.lower().startswith('table '):
        clause_id = clause_id[6:].strip()
    
    # Handle "Figure X.Y" format
    if clause_id.lower().startswith('figure '):
        clause_id = clause_id[7:].strip()
    
    # Handle "Annex X" format
    if clause_id.lower().startswith('annex '):
        clause_id = clause_id[6:].strip()
    
    return clause_id.strip()

def check_clause_match(
    expected_clauses: List[str],
    actual_citations: List[Dict],
    min_similarity: float
) -> tuple[bool, str, float]:
    """
    Check if any expected clause appears in actual citations above similarity threshold
    
    Returns:
        (passed, reason, best_similarity)
    """
    if not actual_citations:
        return False, "no_citations_returned", 0.0
    
    # Normalize all IDs
    normalized_expected = [normalize_clause_id(c) for c in expected_clauses]
    
    best_similarity = 0.0
    matched = False
    
    for citation in actual_citations:
        section = citation.get('section', '')
        clause_id = citation.get('clause_id', '')
        similarity = float(citation.get('similarity', 0.0))
        
        best_similarity = max(best_similarity, similarity)
        
        # Normalize actual clause identifiers
        normalized_section = normalize_clause_id(section)
        normalized_clause = normalize_clause_id(clause_id)
        
        # Check if this citation matches any expected clause
        for expected in normalized_expected:
            if (expected in normalized_section or 
                expected in normalized_clause or
                normalized_section in expected or
                normalized_clause in expected):
                
                if similarity >= min_similarity:
                    matched = True
                    break
        
        if matched:
            break
    
    if matched:
        return True, "match_found", best_similarity
    elif best_similarity > 0 and best_similarity < min_similarity:
        return False, "match_below_similarity_threshold", best_similarity
    else:
        return False, "expected_clause_not_in_topk", best_similarity

def run_validation(
    golden_path: Path,
    api_base: str,
    top_k: int = 5,
    timeout: int = 15,
    pass_rate_threshold: float = 0.90,
    tag: str = "validation"
) -> tuple[bool, Dict]:
    """
    Run full golden dataset validation
    
    Returns:
        (passed, report_dict)
    """
    print("="*60)
    print("ClauseBot RAG - Golden Dataset Validation")
    print("="*60)
    print(f"Golden dataset: {golden_path}")
    print(f"API base: {api_base}")
    print(f"Top-K: {top_k}")
    print(f"Pass rate threshold: {pass_rate_threshold:.1%}")
    print(f"Tag: {tag}")
    print("")
    
    # Load golden dataset
    dataset = load_golden_dataset(golden_path)
    tests = dataset['tests']
    
    print(f"Loaded {len(tests)} tests")
    print("")
    
    # Run tests
    results = []
    passed_count = 0
    failed_count = 0
    total_latency = 0.0
    
    for idx, test in enumerate(tests, 1):
        test_id = test['id']
        query = test['query']
        expected_clauses = test['expected_clauses']
        min_similarity = test.get('min_similarity', 0.70)
        standard = test.get('standard')
        
        print(f"[{idx}/{len(tests)}] {test_id}: {query[:60]}...")
        
        # Query RAG endpoint
        response = query_rag_endpoint(
            api_base=api_base,
            query=query,
            standard=standard,
            top_k=top_k,
            timeout=timeout
        )
        
        latency_ms = response.get('latency_ms', 0.0)
        total_latency += latency_ms
        
        # Check for errors
        if 'error' in response:
            print(f"  ❌ ERROR: {response['error']} - {response.get('detail', '')}")
            failed_count += 1
            results.append({
                'id': test_id,
                'query': query,
                'expected_clauses': expected_clauses,
                'passed': False,
                'reason': f"error_{response['error']}",
                'latency_ms': latency_ms,
                'actual_topk': [],
                'best_similarity': 0.0
            })
            continue
        
        # Extract citations
        citations = response.get('citations', [])
        actual_topk = [c.get('section', '') for c in citations]
        
        # Check match
        passed, reason, best_similarity = check_clause_match(
            expected_clauses=expected_clauses,
            actual_citations=citations,
            min_similarity=min_similarity
        )
        
        if passed:
            print(f"  ✅ PASS (similarity={best_similarity:.3f}, latency={latency_ms:.0f}ms)")
            passed_count += 1
        else:
            print(f"  ❌ FAIL (reason={reason}, similarity={best_similarity:.3f})")
            print(f"     Expected: {expected_clauses}")
            print(f"     Got: {actual_topk}")
            failed_count += 1
        
        results.append({
            'id': test_id,
            'query': query,
            'expected_clauses': expected_clauses,
            'actual_topk': actual_topk,
            'passed': passed,
            'reason': reason,
            'latency_ms': latency_ms,
            'best_similarity': best_similarity,
            'min_similarity': min_similarity
        })
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    # Calculate metrics
    pass_rate = passed_count / len(tests) if tests else 0.0
    avg_latency = total_latency / len(tests) if tests else 0.0
    
    print("")
    print("="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass rate: {pass_rate:.1%}")
    print(f"Average latency: {avg_latency:.0f}ms")
    print("")
    
    validation_passed = pass_rate >= pass_rate_threshold
    
    if validation_passed:
        print(f"✅ VALIDATION PASSED (pass rate {pass_rate:.1%} >= threshold {pass_rate_threshold:.1%})")
    else:
        print(f"❌ VALIDATION FAILED (pass rate {pass_rate:.1%} < threshold {pass_rate_threshold:.1%})")
    
    print("="*60)
    
    # Build report
    report = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'tag': tag,
        'api_base': api_base,
        'golden_dataset': str(golden_path),
        'summary': {
            'total_tests': len(tests),
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate': pass_rate,
            'avg_latency_ms': avg_latency,
            'threshold': pass_rate_threshold,
            'validation_passed': validation_passed
        },
        'results': results
    }
    
    return validation_passed, report

def save_report(report: Dict, output_dir: Path, tag: str):
    """Save JSON and CSV reports"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    # JSON report
    json_path = output_dir / f"golden-report-{tag}-{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"JSON report saved: {json_path}")
    
    # CSV report (for easy review)
    csv_path = output_dir / f"golden-report-{tag}-{timestamp}.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("id,query,expected_clauses,actual_topk,passed,reason,best_similarity,min_similarity,latency_ms\n")
        for result in report['results']:
            f.write(f"{result['id']},")
            f.write(f"\"{result['query']}\",")
            f.write(f"\"{';'.join(result['expected_clauses'])}\",")
            f.write(f"\"{';'.join(result['actual_topk'])}\",")
            f.write(f"{result['passed']},")
            f.write(f"{result['reason']},")
            f.write(f"{result['best_similarity']:.3f},")
            f.write(f"{result['min_similarity']:.3f},")
            f.write(f"{result['latency_ms']:.0f}\n")
    print(f"CSV report saved: {csv_path}")

def main():
    parser = argparse.ArgumentParser(description="Validate RAG retrieval accuracy against golden dataset")
    parser.add_argument("--golden", type=Path, required=True, help="Path to golden dataset JSON")
    parser.add_argument("--api-base", type=str, default="https://clausebot-api.onrender.com", help="API base URL")
    parser.add_argument("--topk", type=int, default=5, help="Number of results to retrieve")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds")
    parser.add_argument("--pass-rate", type=float, default=0.90, help="Minimum pass rate threshold (0.0-1.0)")
    parser.add_argument("--tag", type=str, default="validation", help="Tag for report files")
    parser.add_argument("--output-dir", type=Path, default=Path("ops/reports"), help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Run validation
    try:
        passed, report = run_validation(
            golden_path=args.golden,
            api_base=args.api_base,
            top_k=args.topk,
            timeout=args.timeout,
            pass_rate_threshold=args.pass_rate,
            tag=args.tag
        )
        
        # Save reports
        save_report(report, args.output_dir, args.tag)
        
        # Exit with appropriate code for CI
        sys.exit(0 if passed else 1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()

