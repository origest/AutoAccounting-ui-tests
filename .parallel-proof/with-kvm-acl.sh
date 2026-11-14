#!/usr/bin/env bash
set -euo pipefail
acl="$RUNNER_TEMP/synthetic-dual-kvm.acl"
restore_acl() {
  if [[ -f "$acl" ]]; then
    sudo -n setfacl --restore="$acl" >/dev/null 2>&1 || { echo SUMMARY_KVM_RESTORE_FAILED; return 1; }
    getfacl -p /dev/kvm > "$acl.after" 2>/dev/null || { echo SUMMARY_KVM_RESTORE_FAILED; return 1; }
    cmp -s "$acl" "$acl.after" || { echo SUMMARY_KVM_RESTORE_FAILED; return 1; }
    echo STAGE_KVM_ACL_RESTORED
  fi
}
if [[ "${1:-}" == "--restore" ]]; then
  restore_acl
  exit
fi
python3 .parallel-proof/build-and-test.py --preflight
command -v getfacl >/dev/null
command -v setfacl >/dev/null
[[ -c /dev/kvm && ! -e "$acl" ]]
getfacl -p /dev/kvm > "$acl" 2>/dev/null || { echo SUMMARY_KVM_SNAPSHOT_FAILED; exit 1; }
cleanup() {
  result=$?
  trap - EXIT HUP INT TERM
  restore_acl || result=1
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM
sudo -n setfacl -m "u:$(id -un):rw" /dev/kvm >/dev/null 2>&1 || { echo SUMMARY_KVM_GRANT_FAILED; exit 1; }
[[ -r /dev/kvm && -w /dev/kvm ]]
echo STAGE_KVM_CURRENT_USER_GRANTED
python3 .parallel-proof/build-and-test.py
