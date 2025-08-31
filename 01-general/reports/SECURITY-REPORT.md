# SECURITY-REPORT.md

**Image:** `docker.io/farisagianda/sa-test:v1`  
**Base:** `continuumio/miniconda3:25.3.1-1` (Debian Bookworm)  
**Runtimes:** Python 2.7 (conda env), Python 3.x (conda env), R 4.4 (conda env)  
**Scan date:** 2025-08-31

---

## 1) Scope & Method

- Built image from the hardened Dockerfile (non-root, conda envs for py2/py3/R).  
- Scanned using:
  - **Trivy (image scan)** — OS + application packages + secrets + misconfig.  
  - **Syft (SBOM)** — CycloneDX inventory of packages.  
  - **Grype (SBOM scan)** — CVE detection from SBOM.

Example commands used:
```bash
docker buildx build --load -t docker.io/farisagianda/sa-test:v1 .

trivy image --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL --ignore-unfixed \
  -f table -o reports/trivy.txt docker.io/farisagianda/sa-test:v1
trivy image -f json -o reports/trivy.json docker.io/farisagianda/sa-test:v1

syft docker.io/farisagianda/sa-test:v1 -o cyclonedx-json > reports/sbom.cdx.json

grype sbom:reports/sbom.cdx.json -o table > reports/grype.txt
grype sbom:reports/sbom.cdx.json -o json  > reports/grype.json
```

> Note: Tables below reflect the **Critical/High** items you provided from your most recent runs. See `reports/*` in CI artifacts for full raw output.

---

## 2) Findings (Critical / High)

### 2.1 Trivy — Critical/High (excerpt)
| Severity | CVE | Package | Installed | Fixed In | Ref |
|---|---|---|---|---|---|
| HIGH | CVE-2025-48384 | git | 1:2.39.5-0+deb12u2 | none | https://avd.aquasec.com/nvd/cve-2025-48384 |
| HIGH | CVE-2025-48385 | git | 1:2.39.5-0+deb12u2 | none | https://avd.aquasec.com/nvd/cve-2025-48385 |
| HIGH | CVE-2025-48384 | git-man | 1:2.39.5-0+deb12u2 | none | https://avd.aquasec.com/nvd/cve-2025-48384 |
| HIGH | CVE-2025-48385 | git-man | 1:2.39.5-0+deb12u2 | none | https://avd.aquasec.com/nvd/cve-2025-48385 |
| HIGH | CVE-2025-4802 | libc-bin | 2.36-9+deb12u10 | none | https://avd.aquasec.com/nvd/cve-2025-4802 |
| HIGH | CVE-2025-4802 | libc6 | 2.36-9+deb12u10 | none | https://avd.aquasec.com/nvd/cve-2025-4802 |
| HIGH | CVE-2023-52425 | libexpat1 | 2.5.0-1+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2023-52425 |
| HIGH | CVE-2024-8176 | libexpat1 | 2.5.0-1+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2024-8176 |
| HIGH | CVE-2023-2953 | libldap-2.5-0 | 2.5.13+dfsg-5 | none | https://avd.aquasec.com/nvd/cve-2023-2953 |
| HIGH | CVE-2025-6020 | libpam-modules | 1.5.2-6+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-6020 |
| HIGH | CVE-2025-6020 | libpam-modules-bin | 1.5.2-6+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-6020 |
| HIGH | CVE-2025-6020 | libpam-runtime | 1.5.2-6+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-6020 |
| HIGH | CVE-2025-6020 | libpam0g | 1.5.2-6+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-6020 |
| HIGH | CVE-2023-31484 | libperl5.36 | 5.36.0-7+deb12u2 | none | https://avd.aquasec.com/nvd/cve-2023-31484 |
| HIGH | CVE-2025-8194 | libpython3.11-minimal | 3.11.2-6+deb12u5 | none | https://avd.aquasec.com/nvd/cve-2025-8194 |
| HIGH | CVE-2025-8194 | libpython3.11-stdlib | 3.11.2-6+deb12u5 | none | https://avd.aquasec.com/nvd/cve-2025-8194 |
| CRITICAL | CVE-2025-6965 | libsqlite3-0 | 3.40.1-2+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-6965 |
| CRITICAL | CVE-2025-7458 | libsqlite3-0 | 3.40.1-2+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2025-7458 |
| CRITICAL | CVE-2023-45853 | zlib1g | 1:1.2.13.dfsg-1 | none | https://avd.aquasec.com/nvd/cve-2023-45853 |
| HIGH | CVE-2023-37920 | certifi (py) | 2019.9.11 | 2023.7.22 | https://avd.aquasec.com/nvd/cve-2023-37920 |

### 2.2 Grype — Critical/High (excerpt)
| Severity | CVE | Package | Installed | Fixed In |
|---|---|---|---|---|
| High | CVE-2025-48384 | git | 1:2.39.5-0+deb12u2 | none |
| High | CVE-2025-48384 | git-man | 1:2.39.5-0+deb12u2 | none |
| High | CVE-2023-0286 | openssl | 1.1.1d | 1.0.2zg |
| Critical | CVE-2022-2068 | openssl | 1.1.1d | 1.0.2zf |
| High | CVE-2020-1967 | openssl | 1.1.1d | none |
| High | CVE-2022-1292 | openssl | 1.1.1d | 1.0.2ze |
| Critical | CVE-2018-1000802 | python | 2.7.15 | 2.7.16 |
| High | GHSA-cx63-2mw6-8hw5 | setuptools | 41.4.0 | 70.0.0 |
| Critical | CVE-2019-9636 | python | 2.7.15 | 2.7.17 |
| Critical | CVE-2024-5535 | openssl | 1.1.1d | 1.0.2zk |
| High | CVE-2022-0778 | openssl | 1.1.1d | 1.0.2zd |
| Critical | CVE-2022-48565 | python | 2.7.15 | 3.6.13 |
| High | CVE-2019-5010 | python | 2.7.15 | 2.7.16 |
| Critical | CVE-2019-10160 | python | 2.7.15 | 2.7.17 |
| High | CVE-2018-14647 | python | 2.7.15 | none |
| High | CVE-2024-6232 | python | 2.7.15 | 3.8.20 |
| High | CVE-2023-24329 | python | 2.7.15 | 3.7.17 |
| Critical | CVE-2019-9948 | python | 2.7.15 | 2.7.17 |
| High | CVE-2023-2953 | libldap-2.5-0 | 2.5.13+dfsg-5 | none |
| High | CVE-2019-9674 | python | 2.7.15 | none |
| High | CVE-2023-31484 | libperl5.36 | 5.36.0-7+deb12u2 | none |
| High | CVE-2023-31484 | perl | 5.36.0-7+deb12u2 | none |

> **Observation:** Many findings are from **OS libraries** and the **Python 2.7** environment (EOL).

---

## 3) Risk & Prioritization

**Highest priority to fix:**
1. **CRITICAL OS libs** — `libsqlite3-0`, `zlib1g`. Rebase to a newer base image digest once Debian publishes fixes.
2. **Python 2.7** — do **not** ship in production. If required for tooling/tests, move to a separate “tools” image with restricted egress and read‑only root FS; otherwise update to 2.7.18 for demo parity.
3. **git** CVEs — if not needed at runtime, remove it from the final image; otherwise pick up patched package via base image refresh when available.

**Medium priority:**
- `libc6*`, `libexpat1`, `libpam*`, `libldap` — will clear with base refresh.  
- Avoid pulling large meta‑packages that expand surface area (install only what’s needed).

---

## 4) Remediation Plan (Actionable Changes)

### A) Rebase & Patch OS Layer
- **Rebase** to a newer base image **digest** to inherit patched Debian packages:
  ```dockerfile
  FROM continuumio/miniconda3@sha256:<patched_digest>
  ```
- If a fast fix is available for a specific lib (e.g., sqlite/zlib), apply an in-place upgrade until the next rebase:
  ```dockerfile
  RUN apt-get update &&       apt-get install -y --no-install-recommends --only-upgrade          libsqlite3-0 zlib1g &&       rm -rf /var/lib/apt/lists/*
  ```

### B) Minimize Final Image Surface
- Drop `git` and other build tools from the **final** stage (use multi‑stage build).  
- Keep conda caches clean (`conda clean -afy`) and avoid unnecessary packages.

### C) Python Environments
- **Py3**: keep pinned and current; prefer wheels.  
- **Py2**: isolate to a separate image for legacy tooling, or at least pin to 2.7.18 and restrict runtime privileges/network.

### D) Rebuild & Re‑scan
```bash
docker buildx build --load -t docker.io/farisagianda/sa-test:remediated .
trivy image --severity HIGH,CRITICAL --ignore-unfixed -f table docker.io/farisagianda/sa-test:remediated
syft docker.io/farisagianda/sa-test:remediated -o cyclonedx-json > reports/sbom.remediated.cdx.json
grype sbom:reports/sbom.remediated.cdx.json -o table
```

---

## 5) Supply‑Chain Controls — Avoid Deploying Malicious Packages

**Trusted Sources & Policies**
- Pull images and packages **only from allow‑listed registries/mirrors** (Docker Hub namespace, internal PyPI/conda mirror).  
- Ban direct VCS/URL installs in CI without explicit review.  
- Use **conda‑forge only** with `channel_priority: strict`.

**Lock & Verify**
- **pip**: compile a lockfile with **hashes** and enforce them:
  ```bash
  pip-compile --generate-hashes -o requirements.lock.txt requirements.in
  pip install --require-hashes -r requirements.lock.txt
  ```
- **conda**: generate platform‑specific locks with **conda-lock**:
  ```bash
  conda-lock -f environment.yml -p linux-64
  mamba create -n env --file conda-lock.yml
  ```
- Pin **base images by digest** (immutable), not floating tags.

**SBOM, Signing, & Admission**
- Generate an SBOM (Syft) **each build**; store with artifacts.  
- **Sign** images + SBOM attestations (cosign).  
- Admission policies (Kyverno/Gatekeeper) to require signatures & block images over CVE thresholds.

**Automated Scanning & CI Gates**
- Scan the **image** and **manifests** every build:
  ```bash
  trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 <image>
  grype sbom:sbom.cdx.json --fail-on high
  pip-audit -r requirements-py3.txt
  ```

**Least Privilege at Runtime**
- Run as non‑root (done), drop capabilities, mount **read‑only root FS**, and restrict **egress**.  
- Multi‑stage builds to avoid compilers/headers in production layers.

**Change Management**
- Renovate/Dependabot for controlled updates; **diff SBOMs** on PRs.  
- Keep an **Exception Register** (owner, justification, expiry) for any temporary CVE acceptances.

---

## 6) Executive Summary (what I changed / will change)

- Rebase to a patched base digest to pick up Debian fixes (`libsqlite3-0`, `zlib1g`, `libc`, `libpam`, etc.).  
- Remove `git` and build toolchains from the final image; use multi‑stage build.  
- Keep Py3 current and pinned; **do not ship Py2** in production (or isolate it with strict controls).  
- Rebuild and re‑scan; gate on HIGH/CRITICAL in CI; publish SBOM and sign artifacts.

**Outcome target:** No **CRITICAL** CVEs and fewer **HIGH** issues pending upstream patches; reduced attack surface; supply‑chain safeguards to prevent malicious packages from being deployed.
