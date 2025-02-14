from typing import List, Dict
from tqdm import tqdm
from .report import evaluate_report


def calculate_entity_accuracy(
    ground_truth: List[Dict],
    predictions: List[Dict],
    entity_to_info_map: Dict,
    n_prototype: int,
):
    """
    Calculate accuracy for each entity using the enhanced evaluation system.

    Args:
        ground_truth: List of ground truth report dictionaries
        predictions: List of prediction report dictionaries
        entity_to_info_map: Dictionary mapping entities to their metadata

    Returns:
        Dictionary containing accuracy statistics for each entity
    """
    # Initialise results dictionary
    results = {
        entity: {
            "correct": 0,
            "total": len(ground_truth),
            "incorrect_examples": [],  # Store some examples of incorrect predictions
        }
        for entity in entity_to_info_map.keys()
    }

    for i, (gt_report, pred_report) in enumerate(
        tqdm(
            zip(ground_truth, predictions),
            total=n_prototype,
            desc="Evaluating reports",
            ncols=80,
        )
    ):
        if i == n_prototype:
            break
        # Get scores for this report
        report_scores = evaluate_report(entity_to_info_map, gt_report, pred_report)

        # Update results and collect error examples
        for entity in report_scores:
            results[entity]["correct"] += report_scores[entity]

            # If prediction was wrong, store example (up to 3 examples)
            if (
                report_scores[entity] == 0
                and len(results[entity]["incorrect_examples"]) < 3
            ):
                results[entity]["incorrect_examples"].append(
                    {
                        "ground_truth": gt_report.get(entity),
                        "prediction": pred_report.get(entity),
                    }
                )

    # Calculate percentages and format output with progress bar
    for entity in tqdm(results, desc="Calculating statistics", ncols=80):
        total = results[entity]["total"]
        correct = results[entity]["correct"]
        results[entity]["accuracy"] = f"{(correct/total)*100:.1f}%"

    # Print results
    print("\nAccuracy per entity:")
    print("=" * 80)
    print(f"{'Entity':30} {'Score':15} {'Type':15} {'Example Errors'}")
    print("-" * 80)

    for entity, scores in results.items():
        entity_type = entity_to_info_map[entity][1]
        score_str = f"{scores['correct']}/{n_prototype} ({scores['accuracy']})"

        # Format error examples if any exist
        error_examples = ""
        if scores["incorrect_examples"]:
            example = scores["incorrect_examples"][0]  # Show first error example
            error_examples = (
                f"GT: {example['ground_truth']} → Pred: {example['prediction']}"
            )

        print(f"{entity:30} {score_str:15} {entity_type:15} {error_examples}")

    return results
