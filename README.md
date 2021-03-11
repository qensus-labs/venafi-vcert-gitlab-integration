# Venafi Machine Identity Protection plugin for Jenkins

This plugin integrates [Venafi Machine Identity Protection](https://support.venafi.com/hc/en-us/articles/217991528-Introducing-VCert-API-Abstraction-for-DevOps) with Gitlab-based CI/CD processes.

**Table of contents**

 - [Usage overview](#usage-overview)
 - [Setting up executor hosts (shell and SSH executors only)](#setting-up-executor-hosts-shell-and-ssh-executors-only)
 - [Compatibility](#compatibility)
 - [Operations](#operations)
    - [Venafi Machine Identity Protection: request certificate](#venafi-machine-identity-protection-request-certificate)
       - [Usage with Docker executor](#usage-with-docker-executor)
       - [Usage with shell or SSH executor](#usage-with-shell-or-ssh-executor)
       - [Variables: general](#variables-general)
       - [Variables: subject information](#variables-subject-information)
       - [Variables: output](#variables-output)

## Usage overview

You must already have access to either Venafi TLS Protect (part of the Venafi Trust Protection Platform™), or Venafi DevOpsACCELERATE (part of Venafi Cloud). This Gitlab integration product requires you to specify the connection address and authentication details.

You use this Gitlab integration product by defining, inside your Gitlab CI YAML, jobs call operations provided by this Gitlab integration product.

## Setting up executor hosts (shell and SSH executors only)

If you plan on using this Gitlab integration product in combination with the shell and SSH executors, then you must install the following software on the hosts on which those executors operate. This Gitlab integration product does not take care of installing these prerequisites for you.

 * Install Python >= 3.8. Ensure that it's in PATH.
 * Install our Gitlab integration package: `pip install venafi-vcert-gitlab-integration`

## Compatibility

This product supports the following Gitlab runner executors:

 * Shell
 * SSH
 * Docker

## Operations

### Venafi Machine Identity Protection: request certificate

Requests a pair of certificate + private key. The output is to be written to the specified files, in PEM format.

#### Usage with Docker executor

 * Define a job that calls `venafi-vcert-request-certificate`.
 * Ensure the job operates within the image `quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert-x86_64`.
 * Specify:
    - Connection and authentication details for either a TPP, or for DevOpsACCELERATE.
    - Certificate request parameters.
    - Where to store the output.
 * See the variables reference below.

~~~yaml
request_cert:
  image: quay.io/fullstaq-venafi-gitlab-integration/tlsprotect-vcert-x86_64
  script:
    - venafi-vcert-request-certificate
  variables:
    ## Specify TPP or DevOpsACCELERATE parameters
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
    - Connection and authentication details for either a TPP, or for DevOpsACCELERATE.
    - Certificate request parameters.
    - Where to store the output.
 * See the variables reference below.

~~~yaml
request_cert:
  script:
    - venafi-vcert-request-certificate
  variables:
    ## Specify TPP or DevOpsACCELERATE parameters
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

Required (when using DevOpsACCELERATE):

 * `CLOUD_API_KEY`: The Venafi Cloud API key.

Required (no matter what you use):

 * `ZONE_CONFIG_NAME`: the name of the zone configuration to use.

Optional:

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
