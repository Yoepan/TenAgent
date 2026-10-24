#!/usr/bin/env python3
"""
10-Agent Swarm Project Initializer (v1.0.1)
Installs and bootstraps the 10-Agent Swarm framework into any new project folder.

Usage:
    python setup_project.py "C:\\path\\to\\new-project" [--overwrite]

Files and folders the framework would replace (assets/, dashboard/, .agents/,
AGENTS.md, LICENSE, .gitignore ...) are never overwritten unless --overwrite is
given; the target may not be, or lie inside, the framework checkout itself.
"""

import os
import sys
import shutil
import json

SOURCE_ROOT = os.path.abspath(os.path.dirname(__file__))

def _is_inside(path, parent):
    try:
        return os.path.commonpath([os.path.normcase(path), os.path.normcase(parent)]) == os.path.normcase(parent)
    except ValueError:  # different drives
        return False

def bootstrap_new_project(target_dir, overwrite=False):
    """Install the framework into target_dir; returns False (touching nothing) if refused."""
    target_dir = os.path.abspath(target_dir)
    print(f"\n=======================================================")
    print(f"10-Agent Swarm Framework Initializer")
    print(f"Target Directory: {target_dir}")
    print(f"=======================================================\n")

    if _is_inside(os.path.realpath(target_dir), os.path.realpath(SOURCE_ROOT)):
        print("[ERROR] The target is, or lies inside, the framework checkout itself; "
              "choose a separate folder.")
        return False
    if os.path.exists(target_dir) and not os.path.isdir(target_dir):
        print("[ERROR] The target exists and is not a directory.")
        return False

    # 1. Copy Core Manifestos & Playbooks
    items_to_copy = [
        "AGENTS.md",
        ".agents",
        "dashboard",
        "assets",
        "office.bat",
        "council.py",
        "stream.py",
        "stream.bat",
        "swarm_pipeline.py",
        "favicon.ico",
        "LICENSE",
        ".gitignore"
    ]

    conflicts = [
        item for item in items_to_copy
        if os.path.exists(os.path.join(SOURCE_ROOT, item))
        and os.path.lexists(os.path.join(target_dir, item))
    ]
    # The initial status file is written unconditionally further down.
    if os.path.lexists(os.path.join(target_dir, "specs", "swarm-status.json")):
        conflicts.append("specs/swarm-status.json")
    if conflicts and not overwrite:
        print("[ERROR] These already exist in the target and would be replaced:")
        for item in conflicts:
            print(f"        {item}")
        print("Nothing was changed. Re-run with --overwrite to replace them.")
        return False

    os.makedirs(target_dir, exist_ok=True)

    for item in items_to_copy:
        src = os.path.join(SOURCE_ROOT, item)
        dst = os.path.join(target_dir, item)
        if os.path.exists(src):
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"[OK] Copied directory: {item}/")
            else:
                shutil.copy2(src, dst)
                print(f"[OK] Copied file: {item}")

    # 2. Setup Clean specs/ Directory
    specs_target = os.path.join(target_dir, "specs")
    os.makedirs(os.path.join(specs_target, "prd"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "architecture"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "design"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "database"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "api"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "qa"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "security"), exist_ok=True)
    os.makedirs(os.path.join(specs_target, "reviews"), exist_ok=True)

    # Copy data dictionary template and openapi template if available
    src_specs = os.path.join(SOURCE_ROOT, "specs")
    if os.path.exists(os.path.join(src_specs, "database", "data-dictionary.md")):
        shutil.copy2(
            os.path.join(src_specs, "database", "data-dictionary.md"),
            os.path.join(specs_target, "database", "data-dictionary.md")
        )

    if os.path.exists(os.path.join(src_specs, "swarm-config.example.json")):
        shutil.copy2(
            os.path.join(src_specs, "swarm-config.example.json"),
            os.path.join(specs_target, "swarm-config.example.json")
        )

    # 3. Initialize Fresh Phase 1 Swarm Status
    initial_status = {
        "project": {
            "name": os.path.basename(target_dir),
            "version": "0.1.0",
            "phase": "Phase 1: Discovery & Requirements",
            "overallProgress": 5,
            "lastUpdated": "2026-10-19T02:00:00Z"
        },
        "agents": [
            {
                "id": "01_pm",
                "role": "Product Manager",
                "status": "WORKING",
                "currentTask": "Conducting Client Discovery interview to define MVP feature scope.",
                "processDetail": "Interviewing client: clarifying target users, core business problem, and MVP user stories.",
                "progress": 25,
                "deliverable": "specs/prd/FEATURE_NAME.md"
            },
            {
                "id": "02_arch",
                "role": "System Architect",
                "status": "WAITING",
                "currentTask": "Waiting for PRD feature list to consult tech stack & architecture layers.",
                "processDetail": "Standby to prepare ADR-001 (Clean Architecture layers & boundaries).",
                "progress": 0,
                "deliverable": "specs/architecture/layers.md"
            },
            {
                "id": "03_designer",
                "role": "UI/UX Designer",
                "status": "WAITING",
                "currentTask": "Waiting for PRD to design user flows and UI tokens.",
                "processDetail": "Standby to enforce anti-slop guidelines and design tokens.",
                "progress": 0,
                "deliverable": "specs/design/screen-flows.md"
            },
            {
                "id": "04_dba",
                "role": "Database Engineer",
                "status": "WAITING",
                "currentTask": "Waiting for architecture schema boundary definition.",
                "processDetail": "Standby to design 3NF relational schema and enforce zero duplicate tables.",
                "progress": 0,
                "deliverable": "specs/database/schema.sql"
            },
            {
                "id": "05_backend",
                "role": "Backend Engineer",
                "status": "WAITING",
                "currentTask": "Waiting for OpenAPI contract and database schema lock.",
                "processDetail": "Standby to build domain use cases strictly adhering to OpenAPI contract.",
                "progress": 0,
                "deliverable": "backend/src/"
            },
            {
                "id": "06_client",
                "role": "Client Engineer",
                "status": "WAITING",
                "currentTask": "Waiting for design specs and OpenAPI contract.",
                "processDetail": "Standby for concurrent mobile/web client development.",
                "progress": 0,
                "deliverable": "frontend/src/"
            },
            {
                "id": "07_qa",
                "role": "QA Engineer",
                "status": "IDLE",
                "currentTask": "Standby: Will write test matrix from acceptance criteria.",
                "processDetail": "Waiting for backend/client code implementations.",
                "progress": 0,
                "deliverable": "specs/qa/test-matrix.md"
            },
            {
                "id": "08_security",
                "role": "Security Engineer",
                "status": "IDLE",
                "currentTask": "Standby: Will audit OWASP Top 10 & auth authorization barriers.",
                "processDetail": "Waiting for endpoint routes to run security scanners.",
                "progress": 0,
                "deliverable": "specs/security/audit-report.md"
            },
            {
                "id": "09_devops",
                "role": "DevOps Engineer",
                "status": "IDLE",
                "currentTask": "Standby: Will prepare Docker containerization and CI/CD pipelines.",
                "processDetail": "Waiting for dependency tree finalization.",
                "progress": 0,
                "deliverable": "Dockerfile"
            },
            {
                "id": "10_tech_lead",
                "role": "Technical Lead",
                "status": "WAITING",
                "currentTask": "Gatekeeper standing by to audit diffs and enforce 6 Quality Gates.",
                "processDetail": "Will reject substandard code and approve production merges.",
                "progress": 0,
                "deliverable": "specs/reviews/signoff.md"
            }
        ],
        "logs": [
            {
                "timestamp": "00:00:01",
                "message": "Swarm initialized for new project. Phase 1 Discovery activated."
            }
        ]
    }

    with open(os.path.join(specs_target, "swarm-status.json"), "w", encoding="utf-8") as f:
        json.dump(initial_status, f, indent=2)
    print(f"[OK] Initialized fresh Phase 1 status in: specs/swarm-status.json")

    print("\n-------------------------------------------------------")
    print(f"SUCCESS! Project '{os.path.basename(target_dir)}' is ready.")
    print("-------------------------------------------------------")
    print("\nNext Steps:")
    print(f"1. Open new workspace in Antigravity:")
    print(f"   cd \"{target_dir}\"")
    print(f"2. Launch the 2D Virtual Office Monitor:")
    print(f"   Double-click 'office.bat' or run: python dashboard/serve.py")
    print(f"3. Start Phase 1 Discovery with Agent 01 (Product Manager):")
    print(f"   Prompt: 'Halo, kita mulai project baru ini. Apa yang perlu kita siapkan?'\n")
    return True

def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    overwrite = "--overwrite" in args
    args = [arg for arg in args if arg != "--overwrite"]
    if not args:
        print("Usage: python setup_project.py <target_directory> [--overwrite]")
        print("Example: python setup_project.py C:\\Users\\LENOVO\\Downloads\\projek-baru")
        return 1
    return 0 if bootstrap_new_project(args[0], overwrite=overwrite) else 2

if __name__ == "__main__":
    sys.exit(main())
