#!/usr/bin/env python3
import json
import requests
import csv

def endor_api_get(uri: str, params={}) -> json:
    namespace = "endorlabs"
    ENDOR_API_URL = f"https://api.endorlabs.com/v1/namespaces/{namespace}/{uri}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Request-Timeout": "20",
    }
    response = requests.get(url=ENDOR_API_URL, params=params, headers=headers)
    return response.json()

def get_unique_paths_as_json(
    dependency_dict, node, current_path=None, all_paths=None, visited=None
):
    if current_path is None:
        current_path = []
    if all_paths is None:
        all_paths = []
    if visited is None:
        visited = set()

    # Detect cycles
    if node in visited:
        return all_paths
    visited.add(node)

    # Add the current node to the path
    current_path.append(node)

    # Check if the node is in the dependency dictionary
    if node in dependency_dict:
        # If there are no parents (base case), add the path to all_paths
        if not any(node in deps for deps in dependency_dict.values()):
            all_paths.append(current_path)
        else:
            # Iterate through all items in the dependency dictionary
            for parent, dependencies in dependency_dict.items():
                if node in dependencies:
                    # Recursive call to find parents
                    get_unique_paths_as_json(
                        dependency_dict, parent, current_path[:], all_paths, visited
                    )

    # Remove node from visited after traversal (for other paths)
    visited.remove(node)
    return all_paths

def listDepencyPath():
    url = "https://api.endorlabs.com/v1/auth/api-key"
    payload = {
        "key": "<><><>",
        "secret": "<><><>",
    }
    headers = {"Content-Type": "application/json", "Request-Timeout": "60"}
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    token = response.json().get("token")
    global auth_token
    auth_token = token
    
    csv_file = open("dependency_paths.csv", mode="w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(["Project UUID", "Project Name", "Description", "File Paths", "Level", "Finding UUID", "Summary", "Remediation", "CVSS Score", "Dependency Path"])
    csv_file.close()

    finding_url = "findings?list_parameters.filter=(context.type == 'CONTEXT_TYPE_MAIN' and spec.finding_tags not contains ['FINDING_TAGS_EXCEPTION'] and (spec.finding_tags contains ['FINDING_TAGS_FIX_AVAILABLE'] and spec.finding_tags contains ['FINDING_TAGS_REACHABLE_FUNCTION','FINDING_TAGS_POTENTIALLY_REACHABLE_FUNCTION']) and spec.ecosystem in ['ECOSYSTEM_MAVEN'] and spec.level in ['FINDING_LEVEL_CRITICAL','FINDING_LEVEL_HIGH'] and spec.ecosystem in ['ECOSYSTEM_MAVEN'])&list_parameters.page_size=500&list_parameters.count=false"
    findings = endor_api_get(finding_url)

    while True:
        csv_file = open(f"{findings.get('list', {}).get('response', {}).get('next_page_id')}.csv", mode="a", newline="")
        writer = csv.writer(csv_file)
        for finding in findings.get('list', {}).get('objects', []):
            print("Finding ID ->", finding.get('uuid', ""))
            try:
                project = endor_api_get(f'projects/{finding["spec"]["project_uuid"]}')
                package_version = endor_api_get(f'package-versions/{finding["meta"]["parent_uuid"]}')
                if package_version["spec"]["resolved_dependencies"] is None:
                    writer.writerow([finding["spec"].get('project_uuid', ""), project.get('meta', {}).get('name', ""), finding.get('meta', {}).get('description', ""), finding["spec"].get('dependency_file_paths', ""), finding["spec"].get('level', ""), finding.get('uuid', ""), finding["spec"].get('summary', "").replace('\n', ' '), finding["spec"].get('remediation', ""), finding.get('spec', {}).get('finding_metadata', {}).get('vulnerability', {}).get('spec', {}).get('cvss_v3_severity', {}).get('score', ""), "None"])
                    continue
                dep_paths = get_unique_paths_as_json(package_version["spec"]["resolved_dependencies"]["dependency_graph"], finding["spec"]["target_dependency_package_name"])        
                for path in dep_paths:
                    writer.writerow([
                        finding["spec"].get("project_uuid", ""),
                        project.get('meta', {}).get('name', ""),
                        finding.get('meta', {}).get('description', ""),
                        finding["spec"].get('dependency_file_paths', ""),
                        finding["spec"].get('level', ""),
                        finding.get('uuid', ""),
                        finding["spec"].get('summary', "").replace('\n', ' '),
                        finding["spec"].get('remediation', ""),
                        finding.get('spec', {}).get('finding_metadata', {}).get('vulnerability', {}).get('spec', {}).get('cvss_v3_severity', {}).get('score', ""),
                        path
                    ])
            except KeyError as e:
                print(f"Skipping finding due to missing key: {e}")
        csv_file.close()
        
        finding_url = "findings?list_parameters.filter=(context.type == 'CONTEXT_TYPE_MAIN' and spec.finding_tags not contains ['FINDING_TAGS_EXCEPTION'] and (spec.finding_tags contains ['FINDING_TAGS_FIX_AVAILABLE'] and spec.finding_tags contains ['FINDING_TAGS_REACHABLE_FUNCTION','FINDING_TAGS_POTENTIALLY_REACHABLE_FUNCTION']) and spec.ecosystem in ['ECOSYSTEM_MAVEN'] and spec.level in ['FINDING_LEVEL_CRITICAL','FINDING_LEVEL_HIGH'] and spec.ecosystem in ['ECOSYSTEM_MAVEN'])&list_parameters.page_id=" + str(findings.get('list', {}).get('response', {}).get('next_page_id')) + "&list_parameters.page_size=500&list_parameters.count=false"
        findings = endor_api_get(finding_url)
        
        print("Next Page ID ->", findings.get('list', {}).get('response', {}).get('next_page_id'))
        if findings.get('list', {}).get('response', {}).get('next_page_id') is None:
            break

if __name__ == "__main__":
    listDepencyPath()