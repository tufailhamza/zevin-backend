from fastapi import APIRouter, HTTPException
from app.models import ResearchAlertItem
from typing import List
import json
import os

router = APIRouter()

@router.get("/research-alerts", response_model=List[ResearchAlertItem])
async def get_research_alerts():
    """Get New Racial Justice Research Alert data from JSON file"""
    try:
        # Get the project root directory (parent of app directory)
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)
        
        print(f"\n=== Fetching research alerts ===")
        print(f"Project root: {project_root}")
        print(f"Current working directory: {os.getcwd()}")
        
        # Try to find the JSON file in various locations
        json_file_path = None
        possible_paths = [
            os.path.join(project_root, 'perplexity_analysis_results_20250528_180826.json'),
            os.path.join(os.getcwd(), 'perplexity_analysis_results_20250528_180826.json'),
            'perplexity_analysis_results_20250528_180826.json',
            # Also try with wildcard pattern to find similar files
        ]
        
        # First try exact match
        for path in possible_paths:
            print(f"Checking path: {path}")
            if os.path.exists(path):
                json_file_path = path
                print(f"Found JSON file at: {json_file_path}")
                break
        
        # If not found, try to find any file with similar name
        if not json_file_path:
            print("Exact file not found, searching for similar files...")
            for directory in [project_root, os.getcwd()]:
                if os.path.isdir(directory):
                    print(f"Searching in directory: {directory}")
                    for filename in os.listdir(directory):
                        if 'perplexity' in filename.lower() and filename.endswith('.json'):
                            json_file_path = os.path.join(directory, filename)
                            print(f"Found similar file: {json_file_path}")
                            break
                    if json_file_path:
                        break
        
        if not json_file_path:
            print("WARNING: No JSON file found. Returning empty list.")
            return []
        
        print(f"Loading JSON from: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"Loaded JSON data type: {type(data)}")
        if isinstance(data, list):
            print(f"JSON contains {len(data)} items")
        elif isinstance(data, dict):
            print(f"JSON is a dict with keys: {list(data.keys())}")
        
        # Handle both list and dict formats
        if isinstance(data, dict):
            # If it's a dict, try to find a list inside
            data = data.get('data', data.get('results', [data]))
        if not isinstance(data, list):
            data = [data]
        
        # Convert to list of ResearchAlertItem
        alerts = []
        for item in data:
            # Replace error messages in New_Evidence
            new_evidence = item.get('New_Evidence', '')
            if new_evidence == 'Error processing response':
                new_evidence = 'Unable to retrieve new evidence at this time. Please check back later or contact support.'
            
            alerts.append(ResearchAlertItem(
                Sector=item.get('Sector', ''),
                SDH_Category=item.get('SDH_Category', ''),
                SDH_Indicator=item.get('SDH_Indicator', ''),
                Harm_Description=item.get('Harm_Description', ''),
                Original_Claim_Quantification=item.get('Original_Claim_Quantification'),
                New_Evidence=new_evidence
            ))
        
        print(f"Returning {len(alerts)} research alerts")
        print("=" * 50)
        return alerts
    except FileNotFoundError:
        # Return empty list if file not found
        return []
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading research alerts: {str(e)}")
