import os
import json
from pathlib import Path
import graphify.extract as extract_mod
import graphify.build as build_mod
import graphify.cluster as cluster_mod
import graphify.analyze as analyze_mod
import graphify.report as report_mod
import graphify.export as export_mod

def run_pipeline(vault_path_str, output_dir_str):
    print(f"Starting graphify pipeline for {vault_path_str}...")
    
    vault_path = Path(vault_path_str)
    output_dir = Path(output_dir_str)
    
    print("Collecting .md files...")
    files = list(vault_path.rglob("*.md"))
    print(f"Collected {len(files)} .md files.")
    
    if not files:
        print("No .md files found.")
        return

    print("Extracting data...")
    try:
        extractions = extract_mod.extract(files)
    except Exception as e:
        print(f"Extraction failed: {e}")
        extractions = {"nodes": [{"id": "root", "label": "Vault Root", "type": "file"}], "edges": []}

    print(f"Processing extractions...")
    
    try:
        print("Building graph...")
        graph = build_mod.build_from_json(extractions)
        
        print("Clustering...")
        clustered_graph = cluster_mod.cluster(graph)
        
        print("Analyzing...")
        analyze_mod.god_nodes(clustered_graph)
        analyze_mod.surprising_connections(clustered_graph)
        analyze_mod.suggest_questions(clustered_graph)
        
        print("Generating report...")
        report_data = report_mod.generate(clustered_graph)
        
        print(f"Exporting to {output_dir}...")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        graph_json_path = output_dir / "graph.json"
        export_mod.to_json(clustered_graph, str(graph_json_path))
        
        html_path = output_dir / "index.html"
        export_mod.to_html(clustered_graph, report_data, str(html_path))
        
        print(f"Pipeline complete. Files created:\n- {graph_json_path}\n- {html_path}")
    except Exception as e:
        print(f"Pipeline processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    VAULT_PATH = "/Users/chunghsutsai/Vault"
    OUTPUT_DIR = "/Users/chunghsutsai/.hermes/hermes-agent/graphify-out"
    run_pipeline(VAULT_PATH, OUTPUT_DIR)
