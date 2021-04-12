# Maintenance guide

## Releasing a new version

 1. Ensure [the CI](https://github.com/fullstaq-labs/venafi-vcert-gitlab-integration/actions) is successful.

 2. [Manually run the "CI/CD" workflow](https://github.com/fullstaq-labs/venafi-vcert-gitlab-integration/actions/workflows/ci-cd.yml). Set the `create_release` parameter to `true`. Wait until it finishes. This creates a draft release.

 3. Edit [the draft release](https://github.com/fullstaq-labs/venafi-vcert-gitlab-integration/releases)'s notes and finalize the release.
