# Flora persistent storage runbook

## Render contract

The Flora web service requires its Render persistent disk to be mounted at
`/var/data/flora` and `FLORA_DATA_DIR` to have exactly that value. The checked-in
`render.yaml` declares both settings. A dashboard capacity figure alone does not
prove that a particular running instance has the disk attached.

At startup, find the `flora_storage_probe` event. Confirm that:

* `configured_data_root` and `resolved_data_root` are `/var/data/flora`;
* `is_mount` is true (or, where the platform mounts an ancestor, that
  `existing_path_is_mount` and the filesystem device id match the mount);
* `write_probe_succeeded` and `parent_writable` are true;
* directory uid, gid and mode permit the process uid/gid to write; and
* available bytes **and** available inodes are non-zero.

In a Render shell, corroborate the event with:

```sh
findmnt -T /var/data/flora
df -h /var/data/flora /tmp
df -i /var/data/flora /tmp
stat -c 'path=%n device=%d owner=%u:%g mode=%a' /var/data/flora /var/data/flora/blueprint_import
```

Flora's multipart handler holds the upload body in process memory. Archive
atomic-write temporary files are created beside the final archive under the
persistent root, so receipt does not depend on `/tmp` capacity and the final
rename does not cross filesystems.

## Safe failed-receive cleanup

The receive transaction removes archive and run files that it created when the
package registry record was not committed. Unique atomic-write `.*.tmp` files
are also removed in a `finally` block. To inspect old artifacts before removal:

```sh
find /var/data/flora/blueprint_import -type f -name '.*.tmp' -print
find /var/data/flora/blueprint_import/staging -type f -mtime +1 -print
```

Only remove files matching those temporary patterns after confirming no import
process is running. Do not remove package JSON records, immutable archives,
runs associated with package records, promotion data, memory, or canonical
data.

If receipt fails again, collect the complete `flora_storage_probe`,
`blueprint_package_receive_step`, and persistence-failure events. Preserve the
operation, failing and temporary paths, errno, filesystem device id, mount
flags, uid/gid and mode, writable flag, and total/free/available bytes and
inodes. Compare these values between every deployed instance to detect a failed
or partial disk attachment.
