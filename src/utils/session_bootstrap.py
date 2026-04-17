from pathlib import Path
import yaml


def load_yaml(path):
    path = Path(path)
    if not path.exists():
        print(f"[WARN] Missing YAML file: {path}")
        return None

    with open(path, "r") as f:
        return yaml.safe_load(f)


def check_repo_structure(project_root):
    project_root = Path(project_root)

    expected = {
        "README.md": project_root / "README.md",
        "requirements.txt": project_root / "requirements.txt",
        "src/": project_root / "src",
        "notebooks/": project_root / "notebooks",
        "docs/": project_root / "docs",
        "reports/": project_root / "reports",
        "data/processed/": project_root / "data" / "processed",
        "outputs/": project_root / "outputs",
    }

    print("=" * 80)
    print("Repo structure check")
    print("=" * 80)

    all_ok = True
    for label, path in expected.items():
        exists = path.exists()
        status = "OK" if exists else "MISSING"
        print(f"{label:20} {status:8} {path}")
        if not exists:
            all_ok = False

    return all_ok


def check_data_paths(project_root, extra_data_paths=None):
    project_root = Path(project_root)

    default_candidates = [
        project_root / "data" / "processed" / "features.csv",
        project_root / "data" / "processed" / "processed_demand.csv",
    ]

    if extra_data_paths:
        default_candidates.extend([Path(p) for p in extra_data_paths])

    print("\n" + "=" * 80)
    print("Data availability check")
    print("=" * 80)

    found = []
    for path in default_candidates:
        exists = path.exists()
        status = "FOUND" if exists else "NOT FOUND"
        print(f"{status:10} {path}")
        if exists:
            found.append(path)

    return found


def print_current_status(project_root):
    status_path = Path(project_root) / "docs" / "current_status.yaml"
    status = load_yaml(status_path)

    print("\n" + "=" * 80)
    print("Continuity status")
    print("=" * 80)

    if not status:
        print("No current_status.yaml found.")
        return

    project = status.get("project", {})
    last_session = status.get("last_session", {})
    current_state = status.get("current_state", {})
    issues = status.get("known_issues", [])
    priorities = status.get("next_priorities", [])

    print(f"Project         : {project.get('name', 'N/A')}")
    print(f"Active phase    : {project.get('active_phase', 'N/A')}")
    print(f"Active block    : {project.get('active_block', 'N/A')}")

    print(f"\nLast session    : {last_session.get('date', 'N/A')}")
    print(f"Summary         : {last_session.get('summary', 'N/A')}")
    print(f"Next goal       : {last_session.get('next_goal', 'N/A')}")

    print(f"\nCurrent notebook: {current_state.get('current_notebook', 'N/A')}")
    print(f"Current script  : {current_state.get('current_script', 'N/A')}")
    print(f"Data location   : {current_state.get('current_data_location', 'N/A')}")
    print(f"Priority        : {current_state.get('current_priority', 'N/A')}")

    if issues:
        print("\nKnown issues:")
        for issue in issues:
            print(f" - {issue}")

    if priorities:
        print("\nNext priorities:")
        for item in priorities:
            print(f" - {item}")


def bootstrap_session(project_root, extra_data_paths=None):
    print("\nStarting session bootstrap...\n")
    check_repo_structure(project_root)
    found_data = check_data_paths(project_root, extra_data_paths=extra_data_paths)
    print_current_status(project_root)

    print("\n" + "=" * 80)
    print("Bootstrap summary")
    print("=" * 80)
    print(f"Data files found: {len(found_data)}")
    if found_data:
        for path in found_data:
            print(f" - {path}")
    else:
        print(" - No candidate data files found")

    print("\nSession bootstrap complete.")