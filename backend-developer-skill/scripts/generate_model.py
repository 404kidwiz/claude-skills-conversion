#!/usr/bin/env python3
"""
Database Model Generation Script
Supports multiple ORMs: Sequelize, TypeORM, SQLAlchemy, Django ORM, JPA
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelGenerator:
    """Database model generator for multiple ORMs"""

    def __init__(self, orm: str, config: Dict):
        self.orm = orm.lower()
        self.config = config

        if self.orm not in ['sequelize', 'typeorm', 'sqlalchemy', 'django', 'jpa']:
            raise ValueError(f"Unsupported ORM: {orm}")

    def generate_models(self, output_dir: str):
        """Generate models from schema definition"""
        logger.info(f"Generating {self.orm} models in {output_dir}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        schema = self.config.get('schema', [])

        for entity in schema:
            self._generate_entity_model(entity, output_path)

        logger.info(f"✓ Generated {len(schema)} models")

    def _generate_entity_model(self, entity: Dict, output_path: Path):
        """Generate model for a single entity"""
        name = entity['name']
        fields = entity.get('fields', [])
        relations = entity.get('relations', [])

        logger.info(f"Generating model: {name}")

        if self.orm == 'sequelize':
            self._generate_sequelize_model(name, fields, relations, output_path)
        elif self.orm == 'typeorm':
            self._generate_typeorm_model(name, fields, relations, output_path)
        elif self.orm == 'sqlalchemy':
            self._generate_sqlalchemy_model(name, fields, relations, output_path)
        elif self.orm == 'django':
            self._generate_django_model(name, fields, relations, output_path)
        elif self.orm == 'jpa':
            self._generate_jpa_model(name, fields, relations, output_path)

    def _generate_sequelize_model(self, name: str, fields: List[Dict], relations: List[Dict], output_path: Path):
        """Generate Sequelize model"""
        imports = ['DataTypes, Model, Optional']
        import_str = "from { sequelize, DataTypes, Model, Optional } from 'sequelize';"

        fields_code = []
        for field in fields:
            field_type = self._map_sequelize_type(field['type'])
            attributes = [f"type: DataTypes.{field_type}"]
            if field.get('required'):
                attributes.append("allowNull: false")
            if field.get('unique'):
                attributes.append("unique: true")
            if 'default' in field:
                attributes.append(f"default: {field['default']}")
            fields_code.append(f"    {field['name']}: {{\n        {', '.join(attributes)}\n    }}")

        file_content = f"""import {{ sequelize, {', '.join(import_list)}}}} from 'sequelize';

export interface {name}Attributes {{
{', '.join([f"    {field['name']}: {self._map_ts_type(field['type'])}" for field in fields])}
}}

export interface {name}CreationAttributes extends Optional<{name}Attributes, 'id'> {{}}

export class {name} extends Model<{name}Attributes, {name}CreationAttributes> implements {name}Attributes {{
    public id!: number;
{chr(10).join([f"    public {field['name']}!: {self._map_ts_type(field['type'])};" for field in fields])}

    public readonly createdAt!: Date;
    public readonly updatedAt!: Date;

    static initModel(sequelize: Sequelize): typeof {name} {{
        {name}.init({{
            id: {{
                type: DataTypes.INTEGER,
                autoIncrement: true,
                primaryKey: true,
            }},
{',\n'.join(fields_code)}
        }}, {{
            sequelize,
            tableName: '{name.lower()}s',
            timestamps: true,
        }});

        return {name};
    }}
}}
"""

        with open(output_path / f"{name.lower()}.model.ts", 'w') as f:
            f.write(file_content)

    def _generate_typeorm_model(self, name: str, fields: List[Dict], relations: List[Dict], output_path: Path):
        """Generate TypeORM model"""
        imports = ['Entity', 'PrimaryGeneratedColumn', 'Column']
        if relations:
            imports.extend(['OneToMany', 'ManyToOne', 'ManyToMany', 'JoinTable', 'JoinColumn'])

        imports_str = ', '.join(imports)

        fields_code = []
        for field in fields:
            column_type = self._map_typeorm_type(field['type'])
            decorators = [f"@Column({{ type: '{column_type}' }})"]
            if field.get('required'):
                decorators.append("@Column({ nullable: false })")
            if field.get('unique'):
                decorators.append("@Column({ unique: true })")
            fields_code.append(f"\n    {decorators[0]}\n    public {field['name']}!: {self._map_ts_type(field['type'])};")

        relations_code = []
        for relation in relations:
            rel_type = relation['type']
            target = relation['target']
            if rel_type == 'one-to-many':
                relations_code.append(f"\n    @OneToMany(() => {target}, entity => entity.{name.lower()})\n    public {target.lower()}s!: {target}[];")
            elif rel_type == 'many-to-one':
                relations_code.append(f"\n    @ManyToOne(() => {target}, entity => entity.{target.lower()}s)\n    @JoinColumn({{ name: '{target.lower()}_id' }})\n    public {target.lower()}!: {target};")

        file_content = f"""import {{ {imports_str} }} from 'typeorm';

@Entity('{name.lower()}s')
export class {name} {{
    @PrimaryGeneratedColumn()
    public id!: number;
{''.join(fields_code)}
{''.join(relations_code)}
}}
"""

        with open(output_path / f"{name.lower()}.entity.ts", 'w') as f:
            f.write(file_content)

    def _generate_sqlalchemy_model(self, name: str, fields: List[Dict], relations: List[Dict], output_path: Path):
        """Generate SQLAlchemy model"""
        from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship

        Base = declarative_base()

        file_content = f"""from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class {name}(Base):
    __tablename__ = '{name.lower()}s'

    id = Column(Integer, primary_key=True, index=True)
"""

        for field in fields:
            col_type = self._map_sqlalchemy_type(field['type'])
            col_def = f"    {field['name']} = Column({col_type}"
            if field.get('required'):
                col_def += ", nullable=False"
            if field.get('unique'):
                col_def += ", unique=True"
            col_def += ")"
            file_content += col_def + "\n"

        for relation in relations:
            rel_type = relation['type']
            target = relation['target']
            if rel_type == 'one-to-many':
                file_content += f"    {target.lower()}s = relationship('{target}', back_populates='{name.lower()}')\n"
            elif rel_type == 'many-to-one':
                file_content += f"    {target.lower()} = relationship('{target}', back_populates='{target.lower()}s')\n"

        file_content += "\n    def __repr__(self):\n        return f'<{name} id={{self.id}}>'\n"

        with open(output_path / f"{name.lower()}.py", 'w') as f:
            f.write(file_content)

    def _generate_django_model(self, name: str, fields: List[Dict], relations: List[Dict], output_path: Path):
        """Generate Django model"""
        file_content = f"""from django.db import models
from django.utils import timezone


class {name}(models.Model):
"""

        for field in fields:
            field_type = self._map_django_type(field['type'])
            field_def = f"    {field['name']} = models.{field_type}("
            if field.get('required'):
                field_def += "null=False"
            if field.get('unique'):
                field_def += ", unique=True"
            if 'default' in field:
                field_def += f", default={field['default']}"
            if field.get('max_length'):
                field_def += f", max_length={field['max_length']}"
            field_def += ")"
            file_content += field_def + "\n"

        for relation in relations:
            rel_type = relation['type']
            target = relation['target']
            if rel_type == 'one-to-many':
                file_content += f"    {target.lower()}s = models.ForeignKey('{target}', on_delete=models.CASCADE, related_name='{name.lower()}s')\n"
            elif rel_type == 'many-to-many':
                file_content += f"    {target.lower()}s = models.ManyToManyField('{target}', related_name='{name.lower()}s')\n"

        file_content += """
    class Meta:
        db_table = '{name.lower()}s'
        ordering = ['-id']

    def __str__(self):
        return str(self.id)

    @property
    def created_at(self):
        return timezone.now()
"""

        with open(output_path / f"{name.lower()}.py", 'w') as f:
            f.write(file_content)

    def _generate_jpa_model(self, name: str, fields: List[Dict], relations: List[Dict], output_path: Path):
        """Generate JPA entity"""
        package_path = output_path / 'model'
        package_path.mkdir(parents=True, exist_ok=True)

        imports = ['Entity', 'Id', 'GeneratedValue', 'Column']
        if relations:
            imports.extend(['OneToMany', 'ManyToOne', 'ManyToMany', 'JoinTable', 'JoinColumn'])

        file_content = f"""package com.example.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "{name.toLowerCase()}s")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class {name} {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
"""

        for field in fields:
            col_type = self._map_java_type(field['type'])
            col_def = f"\n    @Column(name = \"{field['name']}\""
            if field.get('required'):
                col_def += ", nullable = false"
            if field.get('unique'):
                col_def += ", unique = true"
            col_def += ")"
            file_content += f"{col_def}\n    private {col_type} {field['name']};"

        for relation in relations:
            rel_type = relation['type']
            target = relation['target']
            if rel_type == 'one-to-many':
                file_content += f"""
    @OneToMany(mappedBy = "{name.lower()}", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<{target}> {target.lower()}s = new ArrayList<>();
"""
            elif rel_type == 'many-to-one':
                file_content += f"""
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "{target.lower()}_id")
    private {target} {target.lower()};
"""

        file_content += "\n}"

        with open(package_path / f"{name}.java", 'w') as f:
            f.write(file_content)

    def _map_sequelize_type(self, field_type: str) -> str:
        type_map = {
            'string': 'STRING',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'float': 'FLOAT',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'DATE',
            'json': 'JSON',
            'uuid': 'UUID'
        }
        return type_map.get(field_type.lower(), 'STRING')

    def _map_typeorm_type(self, field_type: str) -> str:
        type_map = {
            'string': 'varchar',
            'text': 'text',
            'integer': 'int',
            'float': 'float',
            'boolean': 'boolean',
            'date': 'date',
            'datetime': 'timestamp',
            'json': 'json',
            'uuid': 'uuid'
        }
        return type_map.get(field_type.lower(), 'varchar')

    def _map_sqlalchemy_type(self, field_type: str) -> str:
        type_map = {
            'string': 'String(255)',
            'text': 'Text',
            'integer': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'date': 'DateTime',
            'datetime': 'DateTime',
            'json': 'JSON',
            'uuid': 'String(36)'
        }
        return type_map.get(field_type.lower(), 'String(255)')

    def _map_django_type(self, field_type: str) -> str:
        type_map = {
            'string': 'CharField',
            'text': 'TextField',
            'integer': 'IntegerField',
            'float': 'FloatField',
            'boolean': 'BooleanField',
            'date': 'DateField',
            'datetime': 'DateTimeField',
            'json': 'JSONField',
            'uuid': 'UUIDField'
        }
        return type_map.get(field_type.lower(), 'CharField')

    def _map_java_type(self, field_type: str) -> str:
        type_map = {
            'string': 'String',
            'text': 'String',
            'integer': 'Integer',
            'float': 'Double',
            'boolean': 'Boolean',
            'date': 'LocalDate',
            'datetime': 'LocalDateTime',
            'json': 'String',
            'uuid': 'UUID'
        }
        return type_map.get(field_type.lower(), 'String')

    def _map_ts_type(self, field_type: str) -> str:
        type_map = {
            'string': 'string',
            'text': 'string',
            'integer': 'number',
            'float': 'number',
            'boolean': 'boolean',
            'date': 'Date',
            'datetime': 'Date',
            'json': 'object',
            'uuid': 'string'
        }
        return type_map.get(field_type.lower(), 'string')


def main():
    parser = argparse.ArgumentParser(description='Generate database models')
    parser.add_argument('orm', choices=['sequelize', 'typeorm', 'sqlalchemy', 'django', 'jpa'],
                        help='ORM to use')
    parser.add_argument('--schema', required=True, help='Schema JSON file path')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        with open(args.schema, 'r') as f:
            schema = json.load(f)

        generator = ModelGenerator(args.orm, schema)
        generator.generate_models(args.output)
    except FileNotFoundError:
        logger.error(f"Schema file not found: {args.schema}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in schema file: {args.schema}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating models: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
