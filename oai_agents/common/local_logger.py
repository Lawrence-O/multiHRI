"""
Local CSV logger for training metrics when wandb is disabled.
Captures SB3 rollout/train stats and evaluation metrics.
"""
import csv
import json
import time
from pathlib import Path
from collections import defaultdict


class LocalLogger:
    """Logs training and evaluation metrics to CSV files on disk."""

    def __init__(self, log_dir: str, name: str):
        self.log_dir = Path(log_dir) / "logs" / name
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.train_csv = self.log_dir / "training_metrics.csv"
        self.eval_csv = self.log_dir / "eval_metrics.csv"
        self.summary_json = self.log_dir / "summary.json"

        self._train_fields_written = False
        self._eval_fields_written = False
        self._train_writer = None
        self._eval_writer = None
        self._train_file = None
        self._eval_file = None

        self.start_time = time.time()
        self.summary = {
            "name": name,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "best_eval_reward": float("-inf"),
            "best_training_reward": float("-inf"),
            "total_timesteps": 0,
        }

    def log_training(self, agent):
        """Extract and log SB3 PPO training stats from the agent's logger."""
        try:
            sb3_logger = agent.agent.logger
            kv = sb3_logger.name_to_value
        except AttributeError:
            return

        if not kv:
            return

        row = {
            "wall_time": round(time.time() - self.start_time, 1),
            "timesteps": agent.num_timesteps,
        }

        # Flatten SB3 logger key-value pairs
        for key, value in kv.items():
            clean_key = key.replace("/", "_")
            row[clean_key] = round(value, 6) if isinstance(value, float) else value

        self._write_train_row(row)

        # Update summary
        if "rollout_ep_rew_mean" in row:
            self.summary["best_training_reward"] = max(
                self.summary["best_training_reward"], row["rollout_ep_rew_mean"]
            )
        self.summary["total_timesteps"] = agent.num_timesteps

    def log_eval(self, timestep, mean_reward, rew_per_layout, rew_per_layout_per_teamtype=None):
        """Log evaluation results."""
        row = {
            "wall_time": round(time.time() - self.start_time, 1),
            "timesteps": timestep,
            "mean_reward": round(mean_reward, 4),
        }

        for layout, rew in rew_per_layout.items():
            row[f"eval_{layout}"] = round(rew, 4)

        if rew_per_layout_per_teamtype:
            for layout in rew_per_layout_per_teamtype:
                for teamtype, rew in rew_per_layout_per_teamtype[layout].items():
                    row[f"eval_{layout}_{teamtype}"] = round(rew, 4)

        self._write_eval_row(row)

        # Update summary
        if mean_reward > self.summary["best_eval_reward"]:
            self.summary["best_eval_reward"] = mean_reward
        self._save_summary()

    def _write_train_row(self, row):
        if not self._train_fields_written:
            self._train_file = open(self.train_csv, "w", newline="")
            self._train_writer = csv.DictWriter(self._train_file, fieldnames=list(row.keys()), extrasaction="ignore")
            self._train_writer.writeheader()
            self._train_fields_written = True
            self._train_fieldnames = list(row.keys())
        # Handle new fields appearing mid-training (SB3 adds fields after first iteration)
        new_fields = [k for k in row.keys() if k not in self._train_fieldnames]
        if new_fields:
            self._train_file.close()
            self._train_fieldnames.extend(new_fields)
            self._rewrite_csv_with_new_fields(self.train_csv, self._train_fieldnames)
            self._train_file = open(self.train_csv, "a", newline="")
            self._train_writer = csv.DictWriter(self._train_file, fieldnames=self._train_fieldnames, extrasaction="ignore")

        self._train_writer.writerow(row)
        self._train_file.flush()

    def _write_eval_row(self, row):
        if not self._eval_fields_written:
            self._eval_file = open(self.eval_csv, "w", newline="")
            self._eval_writer = csv.DictWriter(self._eval_file, fieldnames=list(row.keys()), extrasaction="ignore")
            self._eval_writer.writeheader()
            self._eval_fields_written = True
            self._eval_fieldnames = list(row.keys())

        new_fields = [k for k in row.keys() if k not in self._eval_fieldnames]
        if new_fields:
            self._eval_file.close()
            self._eval_fieldnames.extend(new_fields)
            self._rewrite_csv_with_new_fields(self.eval_csv, self._eval_fieldnames)
            self._eval_file = open(self.eval_csv, "a", newline="")
            self._eval_writer = csv.DictWriter(self._eval_file, fieldnames=self._eval_fieldnames, extrasaction="ignore")

        self._eval_writer.writerow(row)
        self._eval_file.flush()

    @staticmethod
    def _rewrite_csv_with_new_fields(csv_path, new_fieldnames):
        """Re-read existing CSV and rewrite with expanded fieldnames."""
        rows = []
        if csv_path.exists():
            with open(csv_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=new_fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def _save_summary(self):
        self.summary["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.summary["elapsed_hours"] = round((time.time() - self.start_time) / 3600, 2)
        with open(self.summary_json, "w") as f:
            json.dump(self.summary, f, indent=2)

    def close(self):
        self._save_summary()
        if self._train_file:
            self._train_file.close()
        if self._eval_file:
            self._eval_file.close()
