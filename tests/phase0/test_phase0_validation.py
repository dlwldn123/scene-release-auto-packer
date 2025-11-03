"""Tests de validation Phase 0 - Préparation.

Ces tests vérifient que tous les livrables de la Phase 0 sont présents
et conformes aux critères de Definition of Done.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestPhase0Backup:
    """Tests pour Étape 0.1 : Backup v1/."""

    def test_backup_directory_exists(self) -> None:
        """Vérifier que backup/v1/ existe."""
        backup_path = PROJECT_ROOT / "backup" / "v1"
        assert backup_path.exists(), "backup/v1/ doit exister"
        assert backup_path.is_dir(), "backup/v1/ doit être un répertoire"

    def test_backup_contains_files(self) -> None:
        """Vérifier que backup/v1/ contient des fichiers."""
        backup_path = PROJECT_ROOT / "backup" / "v1"
        files = list(backup_path.iterdir())
        assert len(files) > 0, "backup/v1/ doit contenir des fichiers"

    def test_backup_structure_preserved(self) -> None:
        """Vérifier que la structure v1/ est préservée dans backup/v1/."""
        backup_path = PROJECT_ROOT / "backup" / "v1"
        v1_path = PROJECT_ROOT / "v1"

        # Vérifier fichiers clés présents
        key_files = ["requirements.txt", "README.md"]
        for key_file in key_files:
            backup_file = backup_path / key_file
            v1_file = v1_path / key_file
            if v1_file.exists():
                assert backup_file.exists(), f"{key_file} doit être dans backup/v1/"


class TestPhase0Documentation:
    """Tests pour Étape 0.2 : Documentation Structurée."""

    def test_cdc_exists(self) -> None:
        """Vérifier que docs/cdc.md existe."""
        cdc_path = PROJECT_ROOT / "docs" / "cdc.md"
        assert cdc_path.exists(), "docs/cdc.md doit exister"
        assert cdc_path.stat().st_size > 0, "docs/cdc.md ne doit pas être vide"

    def test_devbook_exists(self) -> None:
        """Vérifier que docs/DEVBOOK.md existe."""
        devbook_path = PROJECT_ROOT / "docs" / "DEVBOOK.md"
        assert devbook_path.exists(), "docs/DEVBOOK.md doit exister"
        assert devbook_path.stat().st_size > 0, "docs/DEVBOOK.md ne doit pas être vide"

    def test_todolist_exists(self) -> None:
        """Vérifier que docs/todolist.md existe."""
        todolist_path = PROJECT_ROOT / "docs" / "todolist.md"
        assert todolist_path.exists(), "docs/todolist.md doit exister"
        assert (
            todolist_path.stat().st_size > 0
        ), "docs/todolist.md ne doit pas être vide"

    def test_prds_directory_exists(self) -> None:
        """Vérifier que docs/PRDs/ existe."""
        prds_path = PROJECT_ROOT / "docs" / "PRDs"
        assert prds_path.exists(), "docs/PRDs/ doit exister"
        assert prds_path.is_dir(), "docs/PRDs/ doit être un répertoire"

    def test_prds_readme_exists(self) -> None:
        """Vérifier que docs/PRDs/README.md existe."""
        prds_readme = PROJECT_ROOT / "docs" / "PRDs" / "README.md"
        assert prds_readme.exists(), "docs/PRDs/README.md doit exister"

    def test_backlog_exists(self) -> None:
        """Vérifier que docs/BACKLOG_AGILE.md existe."""
        backlog_path = PROJECT_ROOT / "docs" / "BACKLOG_AGILE.md"
        assert backlog_path.exists(), "docs/BACKLOG_AGILE.md doit exister"

    def test_project_overview_exists(self) -> None:
        """Vérifier que docs/PROJECT_OVERVIEW.md existe."""
        overview_path = PROJECT_ROOT / "docs" / "PROJECT_OVERVIEW.md"
        assert overview_path.exists(), "docs/PROJECT_OVERVIEW.md doit exister"

    def test_test_plan_exists(self) -> None:
        """Vérifier que docs/TEST_PLAN.md existe."""
        test_plan_path = PROJECT_ROOT / "docs" / "TEST_PLAN.md"
        assert test_plan_path.exists(), "docs/TEST_PLAN.md doit exister"

    def test_risks_register_exists(self) -> None:
        """Vérifier que docs/RISKS_REGISTER.md existe."""
        risks_path = PROJECT_ROOT / "docs" / "RISKS_REGISTER.md"
        assert risks_path.exists(), "docs/RISKS_REGISTER.md doit exister"

    def test_deployment_plan_exists(self) -> None:
        """Vérifier que docs/DEPLOYMENT_PLAN.md existe."""
        deployment_path = PROJECT_ROOT / "docs" / "DEPLOYMENT_PLAN.md"
        assert deployment_path.exists(), "docs/DEPLOYMENT_PLAN.md doit exister"

    def test_mcp_tools_guide_exists(self) -> None:
        """Vérifier que docs/MCP_TOOLS_GUIDE.md existe."""
        mcp_guide_path = PROJECT_ROOT / "docs" / "MCP_TOOLS_GUIDE.md"
        assert mcp_guide_path.exists(), "docs/MCP_TOOLS_GUIDE.md doit exister"


class TestPhase0Environment:
    """Tests pour Étape 0.3 : Configuration Environnement Développement."""

    def test_requirements_txt_exists(self) -> None:
        """Vérifier que requirements.txt existe."""
        req_path = PROJECT_ROOT / "requirements.txt"
        assert req_path.exists(), "requirements.txt doit exister"
        assert req_path.stat().st_size > 0, "requirements.txt ne doit pas être vide"

    def test_requirements_dev_txt_exists(self) -> None:
        """Vérifier que requirements-dev.txt existe."""
        req_dev_path = PROJECT_ROOT / "requirements-dev.txt"
        assert req_dev_path.exists(), "requirements-dev.txt doit exister"
        assert (
            req_dev_path.stat().st_size > 0
        ), "requirements-dev.txt ne doit pas être vide"

    def test_pytest_ini_exists(self) -> None:
        """Vérifier que pytest.ini existe."""
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini doit exister"

    def test_coveragerc_exists(self) -> None:
        """Vérifier que .coveragerc existe."""
        coveragerc = PROJECT_ROOT / ".coveragerc"
        assert coveragerc.exists(), ".coveragerc doit exister"


class TestPhase0TDD:
    """Tests pour Étape 0.4 : Setup TDD."""

    def test_tests_directory_exists(self) -> None:
        """Vérifier que tests/ existe."""
        tests_path = PROJECT_ROOT / "tests"
        assert tests_path.exists(), "tests/ doit exister"
        assert tests_path.is_dir(), "tests/ doit être un répertoire"

    def test_tests_structure_exists(self) -> None:
        """Vérifier que la structure tests/ existe."""
        unit_path = PROJECT_ROOT / "tests" / "unit"
        e2e_path = PROJECT_ROOT / "tests" / "e2e"
        assert (
            unit_path.exists() or e2e_path.exists()
        ), "tests/unit/ ou tests/e2e/ doit exister"

    def test_conftest_exists(self) -> None:
        """Vérifier que tests/conftest.py existe."""
        conftest_path = PROJECT_ROOT / "tests" / "conftest.py"
        assert conftest_path.exists(), "tests/conftest.py doit exister"

    def test_phase0_tests_directory_exists(self) -> None:
        """Vérifier que tests/phase0/ existe."""
        phase0_path = PROJECT_ROOT / "tests" / "phase0"
        assert phase0_path.exists(), "tests/phase0/ doit exister"


class TestPhase0CursorRules:
    """Tests pour Étape 0.5 : Règles Cursor."""

    def test_cursor_rules_directory_exists(self) -> None:
        """Vérifier que .cursor/rules/ existe."""
        rules_path = PROJECT_ROOT / ".cursor" / "rules"
        assert rules_path.exists(), ".cursor/rules/ doit exister"
        assert rules_path.is_dir(), ".cursor/rules/ doit être un répertoire"

    def test_definition_of_done_exists(self) -> None:
        """Vérifier que .cursor/rules/definition-of-done.mdc existe."""
        dod_path = PROJECT_ROOT / ".cursor" / "rules" / "definition-of-done.mdc"
        assert dod_path.exists(), "definition-of-done.mdc doit exister"

    def test_tdd_methodology_exists(self) -> None:
        """Vérifier que .cursor/rules/tdd-methodology.mdc existe."""
        tdd_path = PROJECT_ROOT / ".cursor" / "rules" / "tdd-methodology.mdc"
        assert tdd_path.exists(), "tdd-methodology.mdc doit exister"

    def test_mcp_tools_usage_exists(self) -> None:
        """Vérifier que .cursor/rules/mcp-tools-usage.mdc existe."""
        mcp_path = PROJECT_ROOT / ".cursor" / "rules" / "mcp-tools-usage.mdc"
        assert mcp_path.exists(), "mcp-tools-usage.mdc doit exister"

    def test_documentation_standards_exists(self) -> None:
        """Vérifier que .cursor/rules/documentation-standards.mdc existe."""
        doc_path = PROJECT_ROOT / ".cursor" / "rules" / "documentation-standards.mdc"
        assert doc_path.exists(), "documentation-standards.mdc doit exister"

    def test_testing_requirements_exists(self) -> None:
        """Vérifier que .cursor/rules/testing-requirements.mdc existe."""
        test_req_path = PROJECT_ROOT / ".cursor" / "rules" / "testing-requirements.mdc"
        assert test_req_path.exists(), "testing-requirements.mdc doit exister"

    def test_project_v2_guidelines_exists(self) -> None:
        """Vérifier que .cursor/rules/project-v2-guidelines.mdc existe."""
        proj_path = PROJECT_ROOT / ".cursor" / "rules" / "project-v2.mdc"
        assert proj_path.exists(), "project-v2.mdc doit exister"
