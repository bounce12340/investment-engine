
import os
from pathlib import Path
from graphify.detect import detect
from graphify.extract import extract
from graphify.build import build
from graphify.cluster import cluster
from graphify.analyze import surprising_connections
from graphify.report import generate
from graphify.export import to_json, generate_html

def run_graphify(root_dir_str):
    root_dir = Path(root_dir_str)
    print(f"Starting graphify on {root_dir}...")
    
    # 1. Detect
    detection_result = detect(root_dir)
    
    # The detect() function in v0.4.8 seems to return a dict with a 'files' key 
    # or a list of files plus some stats. Let's handle both.
    if isinstance(detection_result, dict):
        files = detection_result.get('files', [])
    elif isinstance(detection_result, list):
        # Filter out entries that are not Path objects (like stats)
        files = [f for f in detection_result if isinstance(f, Path)]
    else:
        print(f"Unexpected detection result type: {type(detection_result)}")
        return

    print(f"Detected {len(files)} valid files.")
    
    if not files:
        print("No files found to process. Exiting.")
        return

    # 2. Extract
    extractions = []
    for f in files:
        try:
            res = extract(f)
            if res:
                extractions.append(res)
        except Exception as e:
            print(f"Error extracting {f}: {e}")
            
    # 3. Build
    G = build(extractions)
    
    # Safety check: G must be a NetworkX graph, not a dict
    if not hasattr(G, 'number_of_nodes'):
        print("Graph build failed or returned an empty result (not a NetworkX graph).")
        return

    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # 4. Cluster
    G = cluster(G)
    
    # 5. Analyze
    analysis = surprising_connections(G)
    
    # 6. Report
    rep = generate(G, analysis)
    
    # 7. Export
    export_dir = "graphify-out"
    os.makedirs(export_dir, exist_ok=True)
    to_json(G, os.path.join(export_dir, "graph.json"))
    generate_html(G, analysis, rep, os.path.join(export_dir, "index.html"))
    print(f"Knowledge graph exported to {export_dir}")

if __name__ == '__main__':
    run_graphify('/Users/chunghsutsai/Vault')
