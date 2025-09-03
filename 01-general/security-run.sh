#!/usr/bin/env bash
set -euo pipefail
IMG="testimg:tmp"
mkdir -p reports

docker buildx build --load -t "$IMG" .

trivy image --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL --ignore-unfixed \
  -f table -o reports/trivy.txt "$IMG"
trivy image -f json -o reports/trivy.json "$IMG"

syft "$IMG" -o cyclonedx-json > reports/sbom.cdx.json

grype sbom:reports/sbom.cdx.json -o table > reports/grype.txt
grype sbom:reports/sbom.cdx.json -o json  > reports/grype.json

# summaries
jq -r '
  [ .Results[]?.Vulnerabilities[]? ]
  | group_by(.Severity)
  | sort_by(.[0].Severity)
  | map({severity:.[0].Severity, count:length})
' reports/trivy.json > reports/summary.json

jq -r '
  .Results[]?.Vulnerabilities[]?
  | select(.Severity=="CRITICAL" or .Severity=="HIGH")
  | [.Severity, .VulnerabilityID, .PkgName, .InstalledVersion, (.FixedVersion // "none"), .PrimaryURL]
  | @tsv
' reports/trivy.json | head -n 25 > reports/top_trivy.tsv

jq -r '
  .matches[]?
  | select(.vulnerability.severity=="Critical" or .vulnerability.severity=="High")
  | [.vulnerability.severity, .vulnerability.id, .artifact.name, .artifact.version, (.vulnerability.fix.versions[0] // "none")]
  | @tsv
' reports/grype.json | head -n 25 > reports/top_grype.tsv
column -t -s$'\t' reports/top_grype.tsv