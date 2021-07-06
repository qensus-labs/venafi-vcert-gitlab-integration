# Venafi Machine Identity Management integration for Gitlab

This plugin integrates [Venafi Machine Identity Management](https://support.venafi.com/hc/en-us/articles/217991528-Introducing-VCert-API-Abstraction-for-DevOps) with Gitlab-based CI/CD processes.

**Table of contents**

 - [Usage overview](#usage-overview)
 - [Setting up executor hosts (shell and SSH executors only)](#setting-up-executor-hosts-shell-and-ssh-executors-only)
 - [Compatibility](#compatibility)
 - [Operations](#operations)
    - [Request certificate](#request-certificate)
       - [Usage with Docker executor](#usage-with-docker-executor)
       - [Usage with shell or SSH executor](#usage-with-shell-or-ssh-executor)
       - [Variables: general](#variables-general)
       - [Variables: subject information](#variables-subject-information)
       - [Variables: output](#variables-output)
    - [Download previous certificate](#download-previous-certificate)
       - [Usage with Docker executor](#usage-with-docker-executor-1)
       - [Usage with shell or SSH executor](#usage-with-shell-or-ssh-executor-1)
       - [Variables](#variables)
    - [Renewing certificate only when expiration is near](#renewing-certificate-only-when-expiration-is-near)

## Usage overview

You must already have access to either Venafi TLS Protect (part of the Venafi Trust Protection Platform™) or Venafi as a Service. This Gitlab integration product requires you to specify the connection address and authentication details.

You use this Gitlab integration product by defining, inside your Gitlab CI YAML, jobs call operations provided by this Gitlab integration product.

## Setting up executor hosts (shell and SSH executors only)

If you plan on using this Gitlab integration product in combination with the shell and SSH executors, then you must install the following software on the hosts on which those executors operate. This Gitlab integration product does not take care of installing these prerequisites for you.

 * Install Python >= 3.8. Ensure that it's in PATH.
 * Install our Gitlab integration package: `pip install venafi-vcert-gitlab-integration`

## Compatibility

This product requires Gitlab >= 13.9.

This product supports the following Gitlab runner executors:

 * Shell
 * SSH
 * Docker

## Operations

### Request certificate

Requests a pair of certificate + private key. The output is to be written to the specified files, in PEM format.

#### Usage with Docker executor

 * Define a job that calls `venafi-vcert-request-certificate`.
 * Ensure the job operates within the image `quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert`.
 * Specify:
    - Connection and authentication details for either a TPP or for Venafi as a Service.
    - Certificate request parameters.
    - Where to store the output.
 * See the variables reference below.

~~~yaml
request_cert:
  image: quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert
  script:
    - venafi-vcert-request-certificate
  variables:
    ## Specify TPP or Venafi as a Service parameters
    TPP_BASE_URL: https://my-tpp/vedsdk
    TPP_USERNAME: my_username
    # TPP_PASSWORD or TPP_PASSWORD_BASE64 should be set in the UI, with masking enabled.

    ## Specify certificate parameters
    ZONE_CONFIG_NAME: Certificates\\VCert
    COMMON_NAME: yourdomain.com
    ORGANIZATION: orgname
    ORGANIZATIONAL_UNIT: orgunit
    LOCALITY: Amsterdam
    PROVINCE: Noord-Holland
    COUNTRY: NL

    ## Specify where you want to store the output
    CERT_OUTPUT: cert.crt
    CERT_CHAIN_OUTPUT: chain.crt
    PRIV_KEY_OUTPUT: priv.key
  artifacts:
    paths:
      - cert.crt
      - chain.crt
      - priv.key
~~~

#### Usage with shell or SSH executor

 * Define a job that calls `venafi-vcert-request-certificate`.
 * Specify:
    - Connection and authentication details for either a TPP or for Venafi as a Service.
    - Certificate request parameters.
    - Where to store the output.
 * See the variables reference below.

~~~yaml
request_cert:
  script:
    - venafi-vcert-request-certificate
  variables:
    ## Specify TPP or Venafi as a Service parameters
    TPP_BASE_URL: https://my-tpp/vedsdk
    TPP_USERNAME: my_username
    # TPP_PASSWORD or TPP_PASSWORD_BASE64 should be set in the UI, with masking enabled.

    ## Specify certificate parameters
    ZONE_CONFIG_NAME: Certificates\\VCert
    COMMON_NAME: yourdomain.com
    ORGANIZATION: orgname
    ORGANIZATIONAL_UNIT: orgunit
    LOCALITY: Amsterdam
    PROVINCE: Noord-Holland
    COUNTRY: NL

    ## Specify where you want to store the output
    CERT_OUTPUT: cert.crt
    CERT_CHAIN_OUTPUT: chain.crt
    PRIV_KEY_OUTPUT: priv.key
  artifacts:
    paths:
      - cert.crt
      - chain.crt
      - priv.key
~~~

#### Variables: general

Required (when using a TPP):

 * `TPP_BASE_URL`: The TPP's VCert base URL.
 * `TPP_USERNAME`: A login username for the TPP.
 * `TPP_PASSWORD` or `TPP_PASSWORD_BASE64`: The password associated with the login username. You can specify it normally, or in Base64 format. The latter is useful for storing the password in a Gitlab variable, in masked form, because Gitlab can only mask variables whose content only consists of Base64 characters.

Required (when using Venafi as a Service):

 * `CLOUD_API_KEY`: The Venafi as a Service API key.

Required (no matter what you use):

 * `ZONE_CONFIG_NAME`: the name of the zone configuration to use.

Optional:

 * `EXPIRATION_WINDOW`: number of hours before certificate expiry to request a new certificate. We'll check whether the certificate file referenced by `CERT_OUTPUT` already exists, and if so, we'll only proceed with requesting a new certificate if the file's expiry date is within `EXPIRATION_WINDOW` hours. Learn more at [Renewing certificate only when expiration is near](#renewing-certificate-only-when-expiration-is-near).

 * `KEY_TYPE`: either 'RSA' (default) or 'ECDSA'.

 * `DNS_NAMES`: a list of DNS names, as part of the certificate's Alternative Subject Names. Separate multiple values with a comma.

    Example:

    ~~~
    DNS_NAMES: host1.com,host2.com
    ~~~

 * `IP_ADDRESSES`: a list of IP addresses, as part of the certificate's Alternative Subject Names. Separate multiple values with a comma.

    Example:

    ~~~
    IP_ADDRESSES: 127.0.0.1,127.0.0.2
    ~~~

 * `EMAIL_ADDRESSES`: a list of email addresses, as part of the certificate's Alternative Subject Names. Separate multiple values with a comma.

    Example:

    ~~~
    EMAIL_ADDRESSES: a@a.com,b@b.com
    ~~~

#### Variables: subject information

Required:

 * `COMMON_NAME`: the certificate's common name.

Required or optional, depending on the connector's zone configuration:

 * `ORGANIZATION`
 * `ORGANIZATIONAL_UNIT`
 * `LOCALITY`
 * `PROVINCE`
 * `COUNTRY`

#### Variables: output

Required:

 * `PRIV_KEY_OUTPUT`: a path to which the private key should be written.
 * `CERT_OUTPUT`: a path to which the certificate should be written.
 * `CERT_CHAIN_OUTPUT`: a path to which the certificate chain should be written.

### Download previous certificate

Downloads a previously-requested certificate. This works by calling the Gitlab API, searching for a certificate in the latest successful CI build's artifacts. By default, we search in the CI builds of the same project and branch that the pipeline is running on.

If the previous certificate is not found, then it exits with code 30.

This operation is mainly meant to be used for [renewing certificate only when expiration is near](#renewing-certificate-only-when-expiration-is-near). See the example in that section for further explanation of this operation's usage.

#### Usage with Docker executor

 * Define a job that calls `exec venafi-vcert-download-prev-cert`. **Note**: the `exec` keyword is required to ensure that the Gitlab job exits with the correct exit code.
 * Ensure the job operates within the image `quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert`.
 * Ensure a failure due to exit code 30 is allowed.
 * Ensure that the certificate to download, is also published as an artifact.
 * Specify:
    - The name of the CI job that's responsible for calling `venafi-vcert-request-certificate`.
    - The certificate's filename.
 * See the variables reference below.

~~~yaml
download_prev_cert:
  image: quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert
  script:
    - exec venafi-vcert-download-prev-cert
  variables:
    # Specify either one of the following. See the variables reference
    # for info and caveats.
    USE_CI_JOB_TOKEN: 'true'
    # Or set GITLAB_BEARER_TOKEN from the UI, with masking enabled.

    REQUESTER_JOB_NAME: request_cert
    CERT_FILENAME: cert.crt
  allow_failure:
    exit_codes: 30
  artifacts:
    paths:
      - cert.crt
~~~

#### Usage with shell or SSH executor

 * Define a job that calls `exec venafi-vcert-download-prev-cert`. **Note**: the `exec` keyword is required to ensure that the Gitlab job exits with the correct exit code.
 * Ensure a failure due to exit code 30 is allowed.
 * Ensure that the certificate to download, is also published as an artifact.
 * Specify:
    - The name of the CI job that's responsible for calling `venafi-vcert-request-certificate`.
    - The certificate's filename.
 * See the variables reference below.

~~~yaml
download_prev_cert:
  script:
    - exec venafi-vcert-download-prev-cert
  variables:
    # Specify either one of the following. See the variables reference
    # for info and caveats.
    USE_CI_JOB_TOKEN: 'true'
    # Or set GITLAB_BEARER_TOKEN from the UI, with masking enabled.

    REQUESTER_JOB_NAME: request_cert
    CERT_FILENAME: cert.crt
  allow_failure:
    exit_codes: 30
  artifacts:
    paths:
      - cert.crt
~~~

#### Variables

Required: specify an authentication method. Either one of the following must be set:

 * `USE_CI_JOB_TOKEN`: set to `'true'` to use the [Gitlab CI/CD job token](https://docs.gitlab.com/ce/api/README.html#gitlab-cicd-job-token), fetched from the predefined CI variable `CI_JOB_TOKEN`. **Note**: this requires Gitlab Premium >= 13.10.
 * `GITLAB_BEARER_TOKEN`: set to a Personal/Project Access Token, or OAuth2 token.

Required:

 * `REQUESTER_JOB_NAME`: the name of the CI job that's responsible for calling `venafi-vcert-request-certificate`. This operation will search inside that job's artifacts for the certificate.

   We expect that that job publishes the requested certificate as an artifact.

 * `CERT_FILENAME`: the filename of the certificate to search for. This operation will attempt to download this file and store it in the workspace. You **must** also publish this same file as an artifact.

   We expect that the job referenced by `REQUESTER_JOB_NAME`, publishes the requested certificate as an artifact under the specified filename.

Optional:

 * `GITLAB_API_V4_URL`: the base URL of the Gitlab API (version 4) to call. We request artifacts using this API. If not specified, we default to using the predefined CI variable `CI_API_V4_URL`.
 * `PROJECT_PATH`: the name of the Gitlab project in which to search artifacts, e.g. `myusername/myrepo`. If not specified, we default to using the predefined CI variable `CI_PROJECT_PATH`.
 * `BRANCH_NAME`: the name of the branch in which to search artifacts, e.g. `main`. If not specified, we default to using the predefined CI variable `CI_COMMIT_REF_NAME`.

### Renewing certificate only when expiration is near

Normally, `venafi-vcert-request-certificate` requests a certificate every time it's called. Sometimes you only want to request a certificate when it's about to expire. The `EXPIRATION_WINDOW` variable addresses this use case.

`EXPIRATION_WINDOW` expects that you fetch the previously generated certificate, and store it under the same path as specified by `CERT_OUTPUT`. The `EXPIRATION_WINDOW` feature will then check whether that file's expiry date is within `EXPIRATION_WINDOW` hours. If so, or if there is no previously generated certificate, then it'll proceed with requesting a new certificate. Otherwise it does nothing, and logs this decision.

Here's an example of idiomatic usage.

~~~yaml
stages:
 - download_prev_cert
 - request_cert

# Download previous certificate artifact.
download_prev_cert:
  stage: download_prev_cert
  image: quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert
  script:
    - exec venafi-vcert-download-prev-cert
  variables:
    # Specify either one of the following. See the variables reference
    # for info and caveats.
    USE_CI_JOB_TOKEN: 'true'
    # Or set GITLAB_BEARER_TOKEN from the UI, with masking enabled.

    # The name of the job that's responsible for requesting a certificate.
    REQUESTER_JOB_NAME: request_cert
    # The filename of the certificate to download. This matches the
    # artifact filename as published by the `request_cert` job.
    CERT_FILENAME: cert.crt
  allow_failure:
    # If the certificate can't be found, the script exits with code 30.
    # We allow this failure so that `request_cert` will still be called,
    # just without a previous certificate.
    exit_codes: 30
  artifacts:
    paths:
      # If a previous certificate is downloaded, publish it as an
      # artifact so that the `request_cert` job can consume it.
      - cert.crt

# Only request a new certificate if there is no previous certificate,
# or if the previous certificate expires within 48 hours.
request_cert:
  image: quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert
  script:
    - venafi-vcert-request-certificate
  variables:
    TPP_BASE_URL: https://my-tpp/vedsdk
    TPP_USERNAME: my_username
    # TPP_PASSWORD or TPP_PASSWORD_BASE64 should be set in the UI, with masking enabled.

    EXPIRATION_WINDOW: 48

    ZONE_CONFIG_NAME: Certificates\\VCert
    COMMON_NAME: yourdomain.com
    ORGANIZATION: orgname
    ORGANIZATIONAL_UNIT: orgunit
    LOCALITY: Amsterdam
    PROVINCE: Noord-Holland
    COUNTRY: NL

    CERT_OUTPUT: cert.crt
    CERT_CHAIN_OUTPUT: chain.crt
    PRIV_KEY_OUTPUT: priv.key
  artifacts:
    paths:
      # Store the certificate file as an artifact. This file could
      # be a newly requested certificate, or it could be the previous
      # certificate. The next pipeline build will attempt to fetch this
      # file.
      - cert.crt
      - chain.crt
      - priv.key
~~~
