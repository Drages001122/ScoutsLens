import json
import logging
import os
from datetime import datetime
from typing import Any, Callable, Optional

import paramiko

logger = logging.getLogger(__name__)


class DeploymentError(Exception):
    """Base exception for deployment errors"""


class BackupError(DeploymentError):
    """Exception raised when backup fails"""


class RollbackError(DeploymentError):
    """Exception raised when rollback fails"""


class DeploymentState:
    """Manages deployment state for rollback"""

    def __init__(self, state_file: str = "deploy/state.json"):
        self.state_file = state_file
        self.state_dir = os.path.dirname(state_file)
        if self.state_dir and not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load deployment state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return {}
        return {}

    def _save_state(self):
        """Save deployment state to file"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def save_deployment_snapshot(self, snapshot: dict):
        """Save a deployment snapshot"""
        timestamp = datetime.now().isoformat()
        snapshot["timestamp"] = timestamp
        snapshot["id"] = f"deploy_{timestamp.replace(':', '-').replace('.', '-')}"

        if "deployments" not in self.state:
            self.state["deployments"] = []

        self.state["deployments"].append(snapshot)
        self.state["current_deployment"] = snapshot["id"]
        self._save_state()

        return snapshot["id"]

    def get_current_deployment(self) -> Optional[dict]:
        """Get current deployment state"""
        deploy_id = self.state.get("current_deployment")
        if deploy_id:
            for deploy in self.state.get("deployments", []):
                if deploy.get("id") == deploy_id:
                    return deploy
        return None

    def get_previous_deployment(self) -> Optional[dict]:
        """Get previous deployment state for rollback"""
        deploy_id = self.state.get("current_deployment")
        if not deploy_id:
            return None

        deployments = self.state.get("deployments", [])
        for i, deploy in enumerate(deployments):
            if deploy.get("id") == deploy_id and i > 0:
                return deployments[i - 1]
        return None

    def mark_deployment_failed(self, deploy_id: str, error: str):
        """Mark a deployment as failed"""
        for deploy in self.state.get("deployments", []):
            if deploy.get("id") == deploy_id:
                deploy["status"] = "failed"
                deploy["error"] = error
                deploy["failed_at"] = datetime.now().isoformat()
                break
        self._save_state()

    def mark_deployment_success(self, deploy_id: str):
        """Mark a deployment as successful"""
        for deploy in self.state.get("deployments", []):
            if deploy.get("id") == deploy_id:
                deploy["status"] = "success"
                deploy["completed_at"] = datetime.now().isoformat()
                break
        self._save_state()


class ErrorHandler:
    """Centralized error handling for deployment operations"""

    def __init__(self, state: DeploymentState):
        self.state = state
        self.error_callbacks = []

    def add_error_callback(self, callback: Callable[[Exception], None]):
        """Add a callback to be called on error"""
        self.error_callbacks.append(callback)

    def handle_error(self, error: Exception, context: str = "") -> bool:
        """Handle an error and attempt recovery"""
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)

        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")

        return isinstance(error, DeploymentError)

    def create_deployment_snapshot(
        self, hostname: str, remote_dir: str, components: list
    ) -> dict:
        """Create a snapshot before deployment for rollback"""
        return {
            "hostname": hostname,
            "remote_dir": remote_dir,
            "components": components,
            "status": "in_progress",
            "backup_created": False,
        }


class RollbackManager:
    """Manages rollback operations"""

    def __init__(self, state: DeploymentState):
        self.state = state

    def perform_rollback(
        self, hostname: str, username: str, password: str, port: int = 22
    ) -> bool:
        """Perform rollback to previous deployment"""
        previous_deployment = self.state.get_previous_deployment()

        if not previous_deployment:
            logger.error("No previous deployment found for rollback")
            return False

        logger.info(f"Starting rollback to deployment: {previous_deployment.get('id')}")

        try:
            if not self._rollback_database(
                hostname, username, password, port, previous_deployment
            ):
                logger.error("Database rollback failed")
                return False

            if not self._rollback_code(
                hostname, username, password, port, previous_deployment
            ):
                logger.error("Code rollback failed")
                return False

            if not self._restart_service(hostname, username, password, port):
                logger.error("Service restart failed")
                return False

            logger.info("Rollback completed successfully")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False

    def _rollback_database(
        self, hostname: str, username: str, password: str, port: int, deployment: dict
    ) -> bool:
        """Rollback database to previous state"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, password)

            remote_dir = deployment.get("remote_dir", "/var/www/scoutslens")
            backup_dir = f"{remote_dir}/backups"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"{backup_dir}/scoutslens_rollback_backup_{timestamp}.db"
            remote_db = f"{remote_dir}/database/scoutslens.db"

            stdin, stdout, stderr = ssh.exec_command(f"cp {remote_db} {current_backup}")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                logger.error("Failed to backup current database")
                ssh.close()
                return False

            previous_backup = deployment.get("database_backup")
            if previous_backup and os.path.exists(previous_backup):
                stdin, stdout, stderr = ssh.exec_command(
                    f"cp {previous_backup} {remote_db}"
                )
                exit_status = stdout.channel.recv_exit_status()

                if exit_status == 0:
                    logger.info("Database rollback completed")
                    ssh.close()
                    return True

            ssh.close()
            return False

        except Exception as e:
            logger.error(f"Database rollback error: {e}")
            return False

    def _rollback_code(
        self, hostname: str, username: str, password: str, port: int, deployment: dict
    ) -> bool:
        """Rollback code to previous version"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, password)

            remote_dir = deployment.get("remote_dir", "/var/www/scoutslens")
            code_backup = deployment.get("code_backup")

            if code_backup:
                stdin, stdout, stderr = ssh.exec_command(
                    f"test -f {code_backup} && echo 'exists' || echo 'not exists'"
                )
                exit_status, stdout_output, _ = (
                    stdout.channel.recv_exit_status(),
                    stdout.read().decode("utf-8"),
                    stderr.read().decode("utf-8"),
                )

                if "exists" in stdout_output:
                    stdin, stdout, stderr = ssh.exec_command(
                        f"tar -xzf {code_backup} -C {remote_dir}"
                    )
                    exit_status = stdout.channel.recv_exit_status()

                    if exit_status == 0:
                        logger.info("Code rollback completed")
                        ssh.close()
                        return True

            ssh.close()
            return False

        except Exception as e:
            logger.error(f"Code rollback error: {e}")
            return False

    def _restart_service(
        self, hostname: str, username: str, password: str, port: int
    ) -> bool:
        """Restart FastAPI service after rollback"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, port, username, password)

            stdin, stdout, stderr = ssh.exec_command("systemctl restart scoutslens")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                logger.info("Service restarted successfully")
                ssh.close()
                return True

            ssh.close()
            return False

        except Exception as e:
            logger.error(f"Service restart error: {e}")
            return False


def with_error_handling(
    state: DeploymentState, rollback_manager: Optional[RollbackManager] = None
):
    """Decorator for adding error handling to deployment functions"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            deploy_id = kwargs.get("deploy_id")

            try:
                result = func(*args, **kwargs)

                if deploy_id:
                    state.mark_deployment_success(deploy_id)

                return result

            except Exception as e:
                if deploy_id:
                    state.mark_deployment_failed(deploy_id, str(e))

                if rollback_manager and isinstance(e, DeploymentError):
                    logger.info("Attempting rollback...")
                    config = kwargs.get("config", {})
                    if rollback_manager.perform_rollback(
                        config.get("hostname"),
                        config.get("username"),
                        config.get("password"),
                        config.get("port", 22),
                    ):
                        logger.info("Rollback successful")
                    else:
                        logger.error("Rollback failed")

                raise

        return wrapper

    return decorator


def validate_deployment_environment(config: dict) -> bool:
    """Validate deployment environment before starting"""
    required_keys = ["hostname", "username", "password", "remote_project_dir"]

    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration: {key}")
            return False

    return True


def create_deployment_backup(
    hostname: str, username: str, password: str, port: int, remote_dir: str
) -> Optional[str]:
    """Create a backup before deployment"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"{remote_dir}/backups"
        backup_file = f"{backup_dir}/pre_deploy_backup_{timestamp}.tar.gz"

        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {backup_dir}")
        stdout.channel.recv_exit_status()

        stdin, stdout, stderr = ssh.exec_command(
            f"tar -czf {backup_file} -C {remote_dir} backend frontend database"
        )
        exit_status = stdout.channel.recv_exit_status()

        ssh.close()

        if exit_status == 0:
            logger.info(f"Backup created: {backup_file}")
            return backup_file
        else:
            logger.error("Backup creation failed")
            return None

    except Exception as e:
        logger.error(f"Backup error: {e}")
        return None
