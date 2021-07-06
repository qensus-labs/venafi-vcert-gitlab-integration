from dataclasses import dataclass
from typing import List
from venafi_vcert_gitlab_integration import utils
from cryptography import x509
import envparse
import logging
import os.path
import sys
import datetime
import base64
import time
import vcert
import vcert.pem

config_schema = dict(
    TPP_BASE_URL=dict(cast=str, default=None),
    TPP_USERNAME=dict(cast=str, default=None),
    TPP_PASSWORD=dict(cast=str, default=None),
    TPP_PASSWORD_BASE64=dict(cast=str, default=None),

    CLOUD_API_KEY=dict(cast=str, default=None),

    ZONE_CONFIG_NAME=str,
    KEY_TYPE=dict(cast=str, default='RSA'),
    EXPIRATION_WINDOW=dict(cast=int, default=0),
    DNS_NAMES=dict(cast=list, subcast=str, default=()),
    IP_ADDRESSES=dict(cast=list, subcast=str, default=()),
    EMAIL_ADDRESSES=dict(cast=list, subcast=str, default=()),

    COMMON_NAME=str,
    ORGANIZATION=dict(cast=str, default=None),
    ORGANIZATIONAL_UNIT=dict(cast=str, default=None),
    LOCALITY=dict(cast=str, default=None),
    PROVINCE=dict(cast=str, default=None),
    COUNTRY=dict(cast=str, default=None),

    PRIV_KEY_OUTPUT=str,
    CERT_OUTPUT=str,
    CERT_CHAIN_OUTPUT=str,
)


@dataclass(frozen=True)
class RequestCertificateConfig:
    zone_config_name: str
    common_name: str
    priv_key_output: str
    cert_output: str
    cert_chain_output: str

    tpp_base_url: str = None
    tpp_username: str = None
    tpp_password: str = None
    tpp_password_base64: str = None

    cloud_api_key: str = None

    key_type: str = 'RSA'
    expiration_window: int = 0
    dns_names: List[str] = ()
    ip_addresses: List[str] = ()
    email_addresses: List[str] = ()

    organization: str = None
    organizational_unit: str = None
    locality: str = None
    province: str = None
    country: str = None

    @classmethod
    def from_env(cls):
        return cls(**utils.create_dataclass_inputs_from_env(config_schema))


class RequestCertificateCommand:
    def __init__(self, logger, config: RequestCertificateConfig):
        utils.check_one_of_two_config_options_set(
            'TPP_BASE_URL', config.tpp_base_url,
            'CLOUD_API_KEY', config.cloud_api_key
        )
        if config.tpp_base_url is not None:
            utils.check_config_option_set('TPP_USERNAME', config.tpp_username)
            utils.check_one_of_two_config_options_set(
                'TPP_PASSWORD', config.tpp_password,
                'TPP_PASSWORD_BASE64', config.tpp_password_base64
            )
        if config.key_type not in ('RSA', 'ECDSA'):
            raise envparse.ConfigurationError("'KEY_TYPE' may only be 'RSA' or 'ECDSA'.")
        if config.expiration_window < 0:
            raise envparse.ConfigurationError("'EXPIRATION_WINDOW' may not be negative.")

        self.logger = logger
        self.config = config

    def run(self):
        expiration_time = self._get_prev_cert_expiration_time()
        if not self._within_expiration_window(expiration_time):
            self.logger.warning(
                "Previous certificate's expiry time (%s) is not within the" +
                ' expiration window of %d hours. Not requesting a certificate.',
                expiration_time,
                self.config.expiration_window
            )
            return

        conn = self._create_connection_object()
        req = self._create_certificate_request(conn)

        zone_config = conn.read_zone_conf(self.config.zone_config_name)
        req.update_from_zone_config(zone_config)

        self.logger.info('Requesting certificate')
        conn.request_cert(req, self.config.zone_config_name)

        self.logger.info('Retrieving certificate')
        cert = self._retrieve_certificate(conn, req)

        self.logger.info('Writing output')
        self._write_output(req, cert)

    def _get_prev_cert_expiration_time(self):
        if not os.path.exists(self.config.cert_output):
            return None

        with open(self.config.cert_output, 'rb') as f:
            data = f.read()
        try:
            cert = x509.load_pem_x509_certificate(data)
            return cert.not_valid_after
        except Exception as e:
            self.logger.error(
                'Error loading previous certificate (%s): %s',
                self.config.cert_output,
                e
            )
            raise utils.AbortException()

    def _within_expiration_window(self, expiration_time):
        if self.config.expiration_window == 0:
            return True
        elif expiration_time is None:
            self.logger.warning(
                'An expiration window is configured, but the previous certificate' +
                ' (%s) does not exist. Will proceed with requesting a new certificate.',
                self.config.cert_output
            )
            return True
        else:
            threshold = expiration_time - datetime.timedelta(hours=self.config.expiration_window)
            result = datetime.datetime.now() > threshold
            if result:
                self.logger.info(
                    "Previous certificate's expiry time (%s) is within the expiration window of" +
                    ' %d hours. Will proceed with requesting a certificate.',
                    expiration_time,
                    self.config.expiration_window
                )
            return result

    def _create_connection_object(self) -> vcert.CommonConnection:
        if self.config.tpp_base_url is not None:
            return vcert.Connection(
                url=self.config.tpp_base_url,
                user=self.config.tpp_username,
                password=self._get_tpp_password()
            )
        else:
            return vcert.Connection(token=self.config.cloud_api_key)

    def _get_tpp_password(self) -> str:
        if self.config.tpp_password is not None:
            return self.config.tpp_password
        else:
            return str(base64.b64decode(self.config.tpp_password_base64), 'utf-8')

    def _get_key_type(self) -> vcert.KeyType:
        if self.config.key_type == 'RSA':
            return vcert.KeyType(vcert.KeyType.RSA, 4096)
        elif self.config.key_type == 'ECDSA':
            return vcert.KeyType(vcert.KeyType.ECDSA, "p521")
        else:
            raise RuntimeError(f'BUG: unrecognized key type {self.config.key_type}')

    def _create_certificate_request(self, conn: vcert.CommonConnection) -> vcert.CertificateRequest:
        return vcert.CertificateRequest(
            origin='Fullstaq Gitlab integration',
            key_type=self._get_key_type(),
            common_name=self.config.common_name,
            email_addresses=self.config.email_addresses,
            ip_addresses=self.config.ip_addresses,
            organization=self.config.organization,
            organizational_unit=self.config.organizational_unit,
            locality=self.config.locality,
            province=self.config.province,
            country=self.config.country,
        )

    def _retrieve_certificate(self, conn: vcert.CommonConnection, req: vcert.CertificateRequest) -> vcert.pem.Certificate:  # noqa: E501
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            cert = conn.retrieve_cert(req)
            if cert:
                return cert
            else:
                time.sleep(1)

        self.logger.fatal('Timeout retrieving certificate')
        raise utils.AbortException()

    def _write_output(self, req: vcert.CertificateRequest, cert: vcert.pem.Certificate):
        with open(self.config.priv_key_output, 'w') as f:
            f.write(req.private_key_pem)
        with open(self.config.cert_output, 'w') as f:
            f.write(cert.cert)
        with open(self.config.cert_chain_output, 'w') as f:
            f.write("\n".join(cert.chain))


def main():
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
        config = RequestCertificateConfig.from_env()
        command = RequestCertificateCommand(logging.getLogger(), config)
    except envparse.ConfigurationError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    try:
        command.run()
    except utils.AbortException:
        sys.exit(1)


if __name__ == '__main__':
    main()
