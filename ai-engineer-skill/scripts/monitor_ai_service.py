"""
Prompt Template Management System
Manages, versions, and retrieves prompt templates
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    name: str
    template: str
    version: str
    variables: List[str]
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def render(self, **kwargs) -> str:
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template rendering error: {e}")


class PromptManager:
    def __init__(self, templates_dir: Union[str, Path] = "./prompt_templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, List[PromptTemplate]] = {}

        self._load_templates()

    def _load_templates(self):
        for file_path in self.templates_dir.rglob("*.yaml"):
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)

                for template_data in data.get('templates', []):
                    template = PromptTemplate(**template_data)
                    if template.name not in self.templates:
                        self.templates[template.name] = []
                    self.templates[template.name].append(template)

                logger.info(f"Loaded templates from {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def add_template(self, template: PromptTemplate, persist: bool = True):
        if template.name not in self.templates:
            self.templates[template.name] = []

        existing_versions = [t.version for t in self.templates[template.name]]
        if template.version in existing_versions:
            logger.warning(f"Version {template.version} already exists for {template.name}")
            template.version = self._get_next_version(template.name)

        template.updated_at = datetime.utcnow().isoformat()
        self.templates[template.name].append(template)

        if persist:
            self._save_template(template)

        logger.info(f"Added template: {template.name} v{template.version}")

    def _get_next_version(self, name: str) -> str:
        versions = [t.version for t in self.templates.get(name, [])]
        if not versions:
            return "1.0.0"

        try:
            latest = max(versions, key=lambda v: [int(x) for x in v.split('.')])
            major, minor, patch = latest.split('.')
            return f"{major}.{minor}.{int(patch) + 1}"
        except:
            return "1.0.0"

    def _save_template(self, template: PromptTemplate):
        file_path = self.templates_dir / f"{template.name}.yaml"

        data = {'templates': []}
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f) or {'templates': []}

        template_dict = asdict(template)
        data['templates'].append(template_dict)

        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def get_template(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        if name not in self.templates:
            return None

        if version:
            for template in self.templates[name]:
                if template.version == version:
                    return template
        else:
            return self.templates[name][-1]

        return None

    def list_templates(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        if name:
            templates = self.templates.get(name, [])
        else:
            templates = []
            for template_list in self.templates.values():
                templates.extend(template_list)

        return [
            {
                'name': t.name,
                'version': t.version,
                'description': t.description,
                'created_at': t.created_at,
                'updated_at': t.updated_at
            }
            for t in templates
        ]

    def delete_template(self, name: str, version: Optional[str] = None):
        if name not in self.templates:
            return

        if version:
            self.templates[name] = [t for t in self.templates[name] if t.version != version]
        else:
            del self.templates[name]

        logger.info(f"Deleted template: {name}")


def create_default_templates(manager: PromptManager):
    templates = [
        PromptTemplate(
            name="code_explanation",
            template="Explain the following code:\n\n```\n{code}\n```\n\nFocus on: {focus}",
            variables=["code", "focus"],
            description="Explains code with specific focus areas",
            metadata={"category": "code"}
        ),
        PromptTemplate(
            name="summarization",
            template="Summarize the following text in {max_sentences} sentences:\n\n{text}",
            variables=["text", "max_sentences"],
            description="Summarizes text to specified length",
            metadata={"category": "nlp"}
        ),
        PromptTemplate(
            name="question_answering",
            template="Based on the following context:\n\n{context}\n\nAnswer the question: {question}",
            variables=["context", "question"],
            description="Answers questions based on provided context",
            metadata={"category": "qa"}
        )
    ]

    for template in templates:
        manager.add_template(template)


def main():
    manager = PromptManager()

    create_default_templates(manager)

    template = manager.get_template("code_explanation")
    if template:
        rendered = template.render(
            code="print('Hello, World!')",
            focus="functionality and best practices"
        )
        print("Rendered prompt:")
        print(rendered)

    print("\nAvailable templates:")
    for t in manager.list_templates():
        print(f"  - {t['name']} v{t['version']}: {t['description']}")


if __name__ == "__main__":
    main()
