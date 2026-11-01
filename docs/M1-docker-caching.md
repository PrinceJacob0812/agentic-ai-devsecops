# Docker layer caching: results

## What changed
PR #19 added two lines to the build step of build-sbom.yml: cache-from: type=gha and cache-to: type=gha,mode=max.

## Measurement (one pair of runs on main)
| Measure | First run | Second run |
| --- | --- | --- |
| Total workflow time | 2m 50s | 2m 27s |
| Docker build and push | 21s | 6s |

- The second run was started manually on main (build-sbom #65).
- It imported the cache manifest (type=gha), multiple build layers were marked CACHED, and the cache export completed.
- Build step: 15 s faster, about 71.4%. Total: 23 s faster, about 13.5%.

## Reading the result
- The build step gain is explained by the CACHED layers.
- The total gain is small because most of the run is not the Docker build (SBOM, two Grype scans, signing, verification).
- This is one pair of runs, and run times vary by about 30 seconds, so the total difference is indicative, not exact.
- No permissions were added: the GitHub Actions cache uses the run's own token.
