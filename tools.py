from agents import function_tool
import os
import requests

@function_tool
def read_code(filepath: str) -> str:
    """Read the content of a source code file to analyze it.
    Args:
        filepath: The absolute or relative path to the file to read.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: The file '{filepath}' was not found."
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


@function_tool
def search_cve(library_name: str) -> str:
    """Search for known security vulnerabilities (CVEs) for a given library.
    Args:
        library_name: The name of the library or package (e.g., 'requests', 'django').
    """
    try:
        url = "https://api.osv.dev/v1/query"
        payload = {
            "package": {"name": library_name.lower(), "ecosystem": "PyPI"}
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code != 200:
            return f"Service indisponible ou erreur lors de la recherche de vulnérabilités pour {library_name}."
            
        data = response.json()
        vulns = data.get("vulns", [])
        
        if not vulns:
            return f"Aucune vulnérabilité publique connue (CVE) trouvée pour '{library_name}' sur OSV/PyPI."
            
        # Extract at most the top 3 vulnerabilities to avoid exceeding token limits
        report = []
        for v in vulns[:3]:
            cve_id = v.get("id", "Unknown ID")
            summary = v.get("summary", "No summary provided").strip()
            details = v.get("details", "").split("\n")[0] # First line of details
            report.append(f"- {cve_id}: {summary} ({details[:100]}...)")
            
        header = f"Alerte de sécurité pour {library_name} ({len(vulns)} vulnérabilités trouvées, affichant le top 3) :\n"
        return header + "\n".join(report)
        
    except Exception as e:
        return f"Erreur lors de la recherche de CVE pour {library_name}: {str(e)}"

