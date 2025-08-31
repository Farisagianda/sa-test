# SECURITY-REPORT.md

**Image:** `testimg:tmp`  
**Base:** `continuumio/miniconda3:25.3.1-1` (Debian Bookworm)  
**Runtimes:** Python 2.7 (conda env), Python 3.x (conda env), R 4.4 (conda env)  
**Scan date:** 2025-08-30

---

## 1) Scope & Method

- Built image from the provided Dockerfile (non-root, conda envs for py2/py3/R).  
- Scanned locally using:
  - **Trivy (image scan)** — OS + application packages + secrets + misconfig.  
  - **Syft (SBOM)** — CycloneDX inventory of packages.  
  - **Grype (SBOM scan)** — CVE detection from SBOM.

Example commands used:
```bash
docker buildx build --load -t testimg:tmp .

trivy image --scanners vuln,secret,misconfig   --severity HIGH,CRITICAL --ignore-unfixed   -f table -o reports/trivy.txt testimg:tmp
trivy image -f json -o reports/trivy.json testimg:tmp

syft testimg:tmp -o cyclonedx-json > reports/sbom.cdx.json

grype sbom:reports/sbom.cdx.json -o table > reports/grype.txt
grype sbom:reports/sbom.cdx.json -o json  > reports/grype.json
```

> Note: Numbers below reflect the **Critical/High** issues you pasted from your reports. See `reports/*` for the full raw output.

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
| HIGH | CVE-2025-4802 | libc-dev-bin | 2.36-9+deb12u10 | none | https://avd.aquasec.com/nvd/cve-2025-4802 |
| HIGH | CVE-2025-4802 | libc6 | 2.36-9+deb12u10 | none | https://avd.aquasec.com/nvd/cve-2025-4802 |
| HIGH | CVE-2025-4802 | libc6-dev | 2.36-9+deb12u10 | none | https://avd.aquasec.com/nvd/cve-2025-4802 |
| HIGH | CVE-2023-52425 | libexpat1 | 2.5.0-1+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2023-52425 |
| HIGH | CVE-2024-8176 | libexpat1 | 2.5.0-1+deb12u1 | none | https://avd.aquasec.com/nvd/cve-2024-8176 |
| HIGH | CVE-2025-32988 | libgnutls30 | 3.7.9-2+deb12u4 | 3.7.9-2+deb12u5 | https://avd.aquasec.com/nvd/cve-2025-32988 |
| HIGH | CVE-2025-32990 | libgnutls30 | 3.7.9-2+deb12u4 | 3.7.9-2+deb12u5 | https://avd.aquasec.com/nvd/cve-2025-32990 |
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
| HIGH | CVE-2013-7445 | linux-libc-dev | 6.1.147-1 | none | https://avd.aquasec.com/nvd/cve-2013-7445 |
| HIGH | CVE-2019-19449 | linux-libc-dev | 6.1.147-1 | none | https://avd.aquasec.com/nvd/cve-2019-19449 |
| HIGH | CVE-2019-19814 | linux-libc-dev | 6.1.147-1 | none | https://avd.aquasec.com/nvd/cve-2019-19814 |

### 2.2 Grype — Critical/High (excerpt)
| Severity | CVE | Package | Installed | Fixed In |
|---|---|---|---|---|
| High | CVE-2025-48384 | git | 1:2.39.5-0+deb12u2 | none |
| High | CVE-2025-48384 | git-man | 1:2.39.5-0+deb12u2 | none |
| Critical | CVE-2018-1000802 | python | 2.7.15 | 2.7.16 |
| High | GHSA-cx63-2mw6-8hw5 | setuptools | 41.4.0 | 70.0.0 |
| Critical | CVE-2019-9636 | python | 2.7.15 | 2.7.17 |
| Critical | CVE-2024-5535 | openssl | 1.1.1w | 1.0.2zk |
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
| High | CVE-2023-31484 | perl-base | 5.36.0-7+deb12u2 | none |
| High | CVE-2023-31484 | perl-modules-5.36 | 5.36.0-7+deb12u2 | none |
| High | CVE-2022-0391 | python | 2.7.15 | 3.6.14 |
| High | CVE-2024-4032 | python | 2.7.15 | 3.8.20 |
| High | CVE-2019-16056 | python | 2.7.15 | none |
| High | CVE-2023-52425 | libexpat1 | 2.5.0-1+deb12u1 | none |
| High | CVE-2017-17522 | python | 2.7.15 | none |
| High | CVE-2024-7592 | python | 2.7.15 | 3.8.20 |

> **Observation:** A large share of findings come from **OS libraries** and the **Python 2.7** environment (which is end‑of‑life). Also, `r-essentials` pulls in a broad Jupyter stack, expanding the surface area.

---

## 3) Risk & Prioritization

**Highest priority to fix:**
1. **CRITICAL OS libs** (e.g., `libsqlite3-0`) — rebase to a newer base image digest or update via APT when upstream publishes patched packages.
2. **Python 2.7** findings — do **not** ship Py2 in production images. If required for tests, isolate to a separate “tools” image with restricted egress and read‑only root FS; otherwise upgrade to the latest available 2.7 build (2.7.18) for the demo.
3. **`git` CVEs** — if git isn’t needed at runtime, remove it; otherwise rebase/upgrade to a fixed package when available.
4. **`libgnutls30` Highs** — explicitly upgrade to `…deb12u5` (fixed per Trivy).

**Medium priority:**
- `libexpat1`, `libc6*`, `libpam*`, `libldap` — pick up fixes by rebasing to a newer Debian snapshot/digest as patches land.
- Remove build toolchains (`build-essential`, `linux-libc-dev`) from the **final image** (multi‑stage build).

---

## 4) Remediation Plan (Actionable Changes)

### A) Rebase & Patch OS Layer
- **Prefer rebasing the base image to a newer digest** to pick up patched Debian packages:
  ```dockerfile
  FROM continuumio/miniconda3@sha256:<newer_patched_digest>
  ```
- If immediate patching is needed for a known fixed package (e.g., `libgnutls30`):
  ```dockerfile
  RUN apt-get update &&       apt-get install -y --no-install-recommends --only-upgrade libgnutls30 &&       rm -rf /var/lib/apt/lists/*
  ```

### B) Minimize Final Image Surface
- Remove `git` from APT install unless required at runtime.
- Use a **multi‑stage build**: keep `build-essential` and headers only in the build stage; copy the conda envs into the final stage.
- For R, avoid the large `r-essentials` meta‑package unless needed; install targeted packages only:
  ```dockerfile
  RUN mamba create -y -n r-env r-base=4.4 &&       mamba install -y -n r-env -c conda-forge r-data.table r-ggplot2 r-httr &&       conda clean -afy
  ```

### C) Python Environments
- **Py3**: keep versions pinned and current; prefer wheels to avoid compiles.
- **Py2**: policy decision — **do not ship Py2 to prod**. For the demo image, pin to the latest available 2.7 build:
  ```dockerfile
  RUN mamba create -y -n py2 python=2.7.18 pip && conda clean -afy
  ```
  If Py2 is business‑critical, isolate it into a separate image with network egress restrictions and read‑only root FS.

### D) Rebuild & Re‑scan
```bash
docker buildx build --load -t testimg:remediated .
trivy image --severity HIGH,CRITICAL --ignore-unfixed -f table testimg:remediated
syft testimg:remediated -o cyclonedx-json > reports/sbom.remediated.cdx.json
grype sbom:reports/sbom.remediated.cdx.json -o table
```

---

## 5) Supply‑Chain Controls — Avoid Deploying Malicious Packages

**Trusted Sources & Policies**
- Pull images and packages **only from allow‑listed registries/mirrors** (Docker registry namespace, internal PyPI/conda mirrors).  
- Disallow `latest` tags and direct VCS/URL installs in CI without explicit review.  
- Use **conda‑forge only** with `channel_priority: strict` (no mixing with `defaults`).

**Lock & Verify**
- **pip**: compile a lockfile with **hashes** and enforce them:
  ```bash
  pip-compile --generate-hashes -o requirements.lock.txt requirements.in
  pip install --require-hashes -r requirements.lock.txt
  ```
- **conda**: create platform‑specific locks (exact builds) with **conda-lock**:
  ```bash
  conda-lock -f environment.yml -p linux-64
  mamba create -n env --file conda-lock.yml
  ```
- Pin **base images by digest** (immutable), not floating tags.

**SBOM, Signing, & Admission**
- Generate an SBOM (Syft) **for every build** and store it with artifacts.  
- **Sign** images and SBOM attestations (cosign).  
- Enforce admission policies (Kyverno/Gatekeeper) to require signatures and to block images over CVE thresholds (e.g., no CRITICAL).

**Automated Scanning & CI Gates**
- Scan both the **image** and the **dependency manifests** on every build:
  ```bash
  trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 <image>
  grype sbom:sbom.cdx.json --fail-on high
  pip-audit -r requirements-py3.txt
  ```

**Least Privilege at Runtime**
- Run as non‑root (already in Dockerfile), drop Linux capabilities, mount **read‑only root FS**, and restrict **network egress**.  
- Use multi‑stage builds to remove compilers/headers from production images.

**Change Management**
- Use Renovate/Dependabot for controlled bumps; **diff SBOMs** on PRs.  
- Maintain an **Exception Register** for any temporary CVE acceptances (owner, justification, expiry).

---

## 6) Executive Summary (what I changed / will change)

- Rebase to a newer base digest to pick up patched Debian packages (addresses `libsqlite3-0`, `libexpat1`, `libc`, `libpam`, etc.).  
- Remove `git` and dev toolchains from the **final** image; use multi‑stage.  
- Upgrade `libgnutls30` to the fixed `…deb12u5` build.  
- Keep Py3 current and pinned; **exclude Py2 from production** (or isolate it with strict controls).  
- Rebuild and re‑scan; gate on HIGH/CRITICAL in CI; publish SBOM and sign artifacts.

**Outcome target:** No **CRITICAL** CVEs and a reduced set of **HIGH** findings awaiting upstream patches; minimized attack surface; supply‑chain protections to prevent malicious packages from being deployed.
