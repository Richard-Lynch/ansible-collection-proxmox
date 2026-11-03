# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Reconcile a cluster-wide nightly vzdump backup job via pvesh",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_vzdump_job_tag": OptionSpec(
                    type="str",
                    required=False,
                    description=["Stable tag in the job comment (idempotency key)."],
                ),
                "proxmox_vzdump_comment": OptionSpec(
                    type="str", required=False, description=["Full job comment (contains the tag)."]
                ),
                "proxmox_vzdump_storage": OptionSpec(
                    type="str",
                    required=False,
                    description=["Backup-capable storage (content=backup)."],
                ),
                "proxmox_vzdump_schedule": OptionSpec(
                    type="str",
                    required=False,
                    description=["Backup schedule (systemd calendar / HH:MM)."],
                ),
                "proxmox_vzdump_all": OptionSpec(
                    type="bool", required=False, description=["Back up all guests."]
                ),
                "proxmox_vzdump_exclude": OptionSpec(
                    type="str", required=False, description=["Comma-separated VMIDs to exclude."]
                ),
                "proxmox_vzdump_mode": OptionSpec(
                    type="str", required=False, description=["snapshot|suspend|stop."]
                ),
                "proxmox_vzdump_compress": OptionSpec(
                    type="str", required=False, description=["Compression (zstd/lzo/gzip)."]
                ),
                "proxmox_vzdump_mailnotification": OptionSpec(
                    type="str", required=False, description=["always|failure."]
                ),
                "proxmox_vzdump_notes_template": OptionSpec(
                    type="str", required=False, description=["PVE note template."]
                ),
                "proxmox_vzdump_keep_daily": OptionSpec(
                    type="int", required=False, description=["Retention: keep-daily."]
                ),
                "proxmox_vzdump_keep_weekly": OptionSpec(
                    type="int", required=False, description=["Retention: keep-weekly."]
                ),
                "proxmox_vzdump_keep_monthly": OptionSpec(
                    type="int", required=False, description=["Retention: keep-monthly."]
                ),
                "proxmox_vzdump_enabled": OptionSpec(
                    type="bool",
                    required=False,
                    default=True,
                    description=["Enable the job on create."],
                ),
            },
        )
    }
)
