"""Unit tests for resume_parser.utils.skills_list_loader."""

import json
import pytest
from resume_parser.utils.skills_list_loader import load_skills, load_roles


class TestLoadSkillsDefault:
    """Tests using the bundled skills_master.json."""

    def test_returns_dict(self):
        data = load_skills()
        assert isinstance(data, dict)

    def test_has_all_technical_skills_key(self):
        data = load_skills()
        assert "ALL_TECHNICAL_SKILLS" in data, "Top-level key 'ALL_TECHNICAL_SKILLS' is missing"

    def test_all_technical_skills_is_dict(self):
        data = load_skills()
        assert isinstance(data["ALL_TECHNICAL_SKILLS"], dict)

    def test_has_roles_key(self):
        data = load_skills()
        assert "ROLES" in data, "Top-level key 'ROLES' is missing"

    def test_roles_is_dict(self):
        data = load_skills()
        assert isinstance(data["ROLES"], dict)

    def test_at_least_one_category(self):
        data = load_skills()
        assert data["ALL_TECHNICAL_SKILLS"], "ALL_TECHNICAL_SKILLS should not be empty"

    def test_skill_entries_have_name(self):
        data = load_skills()
        for category, skills in data["ALL_TECHNICAL_SKILLS"].items():
            for skill in skills:
                assert "name" in skill, f"Skill in '{category}' is missing 'name' key"

    def test_at_least_one_role(self):
        data = load_skills()
        assert data["ROLES"], "ROLES should not be empty"


class TestLoadSkillsCustomPath:
    """Tests using a minimal custom JSON file."""

    def test_custom_file_loaded(self, tmp_path):
        payload = {
            "ALL_TECHNICAL_SKILLS": {
                "Languages": [{"name": "Python", "aliases": ["py"]}]
            },
            "ROLES": {
                "Backend Engineer": ["Languages"]
            }
        }
        p = tmp_path / "test_skills.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        data = load_skills(str(p))
        assert data["ALL_TECHNICAL_SKILLS"]["Languages"][0]["name"] == "Python"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_skills(str(tmp_path / "nonexistent.json"))


class TestLoadRoles:
    def test_returns_list(self):
        roles = load_roles()
        assert isinstance(roles, list)

    def test_roles_are_strings(self):
        for role in load_roles():
            assert isinstance(role, str), f"Role '{role}' is not a string"

    def test_at_least_one_role(self):
        assert load_roles(), "load_roles() should return at least one role"

    def test_custom_path_returns_correct_roles(self, tmp_path):
        payload = {
            "ALL_TECHNICAL_SKILLS": {},
            "ROLES": {"Data Scientist": [], "ML Engineer": []}
        }
        p = tmp_path / "roles.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        roles = load_roles(str(p))
        assert set(roles) == {"Data Scientist", "ML Engineer"}
