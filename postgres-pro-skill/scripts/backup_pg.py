"""
PostgreSQL Backup and Restore
Comprehensive backup strategies for PostgreSQL
"""

import logging
import subprocess
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import gzip
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: Optional[str] = None
    database: Optional[str] = None
    backup_dir: str = "./backups"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'PostgresConfig':
        return cls(**config)


class PostgresBackupManager:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self.backup_dir = Path(config.backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _build_env(self) -> Dict[str, str]:
        env = os.environ.copy()

        if self.config.password:
            env['PGPASSWORD'] = self.config.password

        return env

    def build_pg_dump_command(
        self,
        database: str,
        output_file: str,
        format_type: str = "c",
        compression: int = 9
    ) -> List[str]:
        command = [
            "pg_dump",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            "-F", format_type,
            "-Z", str(compression),
            "-f", output_file,
            "-v",
            database
        ]

        return command

    def backup_database(
        self,
        database: str,
        backup_name: Optional[str] = None,
        compress: bool = True
    ) -> Dict[str, Any]:
        logger.info(f"Starting backup for database: {database}")

        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{database}_{timestamp}"

        if compress:
            output_file = self.backup_dir / f"{backup_name}.dump.gz"
            temp_file = self.backup_dir / f"{backup_name}.dump"
        else:
            output_file = self.backup_dir / f"{backup_name}.dump"

        start_time = datetime.now()

        try:
            # Create dump
            command = self.build_pg_dump_command(
                database=database,
                output_file=str(temp_file)
            )

            result = subprocess.run(
                command,
                env=self._build_env(),
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"pg_dump completed: {result.stdout}")

            # Compress if needed
            if compress:
                self._compress_file(temp_file, output_file)
                temp_file.unlink()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            file_size = output_file.stat().st_size

            backup_info = {
                'database': database,
                'backup_name': backup_name,
                'file_path': str(output_file),
                'file_size': file_size,
                'compressed': compress,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'status': 'success'
            }

            self._log_backup(backup_info)
            logger.info(f"Backup completed in {duration:.2f}s, size: {file_size:,} bytes")

            return backup_info

        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise

    def _compress_file(self, input_file: Path, output_file: Path):
        logger.info(f"Compressing {input_file.name}")

        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                f_out.writelines(f_in)

        logger.info(f"Compression completed")

    def backup_all_databases(
        self,
        backup_name: Optional[str] = None,
        compress: bool = True
    ) -> Dict[str, Any]:
        databases = self._list_databases()

        backups = []
        for database in databases:
            if database not in ['postgres', 'template0', 'template1']:
                backup_info = self.backup_database(database, backup_name, compress)
                backups.append(backup_info)

        return {
            'timestamp': datetime.now().isoformat(),
            'databases_backed_up': len(backups),
            'backups': backups
        }

    def _list_databases(self) -> List[str]:
        command = [
            "psql",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            "-d", "postgres",
            "-t",
            "-c", "SELECT datname FROM pg_database WHERE datistemplate = false;"
        ]

        result = subprocess.run(
            command,
            env=self._build_env(),
            capture_output=True,
            text=True,
            check=True
        )

        databases = [db.strip() for db in result.stdout.strip().split('\n') if db.strip()]
        return databases

    def restore_database(
        self,
        database: str,
        backup_file: str,
        create_if_not_exists: bool = True
    ) -> Dict[str, Any]:
        logger.info(f"Restoring database: {database} from {backup_file}")

        backup_path = Path(backup_file)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        # Decompress if needed
        if backup_path.suffix == '.gz':
            temp_file = backup_path.with_suffix('')
            self._decompress_file(backup_path, temp_file)
            input_file = temp_file
        else:
            input_file = backup_path

        start_time = datetime.now()

        try:
            if create_if_not_exists:
                self._create_database(database)

            # Restore
            command = [
                "pg_restore",
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", self.config.user,
                "-d", database,
                "-v",
                str(input_file)
            ]

            result = subprocess.run(
                command,
                env=self._build_env(),
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Restore completed: {result.stdout}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            restore_info = {
                'database': database,
                'backup_file': str(backup_file),
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'status': 'success'
            }

            logger.info(f"Restore completed in {duration:.2f}s")
            return restore_info

        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {e.stderr}")
            raise

    def _decompress_file(self, input_file: Path, output_file: Path):
        logger.info(f"Decompressing {input_file.name}")

        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                f_out.writelines(f_in)

    def _create_database(self, database: str):
        command = [
            "psql",
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.user,
            "-d", "postgres",
            "-c", f"CREATE DATABASE {database};"
        ]

        subprocess.run(command, env=self._build_env(), check=True)
        logger.info(f"Created database: {database}")

    def _log_backup(self, backup_info: Dict[str, Any]):
        log_file = self.backup_dir / "backup_history.json"

        history = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                history = json.load(f)

        history.append(backup_info)

        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)

    def list_backups(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        log_file = self.backup_dir / "backup_history.json"

        if not log_file.exists():
            return []

        with open(log_file, 'r') as f:
            history = json.load(f)

        if database:
            return [b for b in history if b['database'] == database]

        return history

    def delete_old_backups(self, days: int = 30):
        logger.info(f"Deleting backups older than {days} days")

        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        history = self.list_backups()
        deleted = 0

        for backup in history:
            backup_date = datetime.fromisoformat(backup['timestamp'])
            if backup_date < cutoff_date:
                backup_file = Path(backup['file_path'])
                if backup_file.exists():
                    backup_file.unlink()
                    deleted += 1
                    logger.info(f"Deleted: {backup_file.name}")

        logger.info(f"Deleted {deleted} old backups")


def main():
    config = PostgresConfig(
        host="localhost",
        user="postgres",
        password="your_password",
        backup_dir="./pg_backups"
    )

    manager = PostgresBackupManager(config)

    # Backup a database
    backup_info = manager.backup_database("mydb", compress=True)
    print(f"Backup info: {backup_info}")

    # List backups
    backups = manager.list_backups()
    print(f"Total backups: {len(backups)}")


if __name__ == "__main__":
    main()
