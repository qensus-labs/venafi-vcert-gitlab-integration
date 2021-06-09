from dataclasses import dataclass
from venafi_vcert_gitlab_integration import utils
import envparse
import requests
import urllib.parse
import logging
import sys
import os


@dataclass(frozen=True)
class DownloadPrevCertConfig:
    gitlab_api_v4_url: str
    project_path: str
    branch_name: str
    requester_job_name: str
    cert_filename: str

    use_ci_job_token: bool = False
    gitlab_bearer_token: str = None

    @classmethod
    def from_env(cls):
        return cls(
            gitlab_api_v4_url=cls._getenv('GITLAB_API_V4_URL', 'CI_API_V4_URL'),
            project_path=cls._getenv('PROJECT_PATH', 'CI_PROJECT_PATH'),
            branch_name=cls._getenv('BRANCH_NAME', 'CI_COMMIT_REF_NAME'),
            requester_job_name=cls._getenv('REQUESTER_JOB_NAME'),
            cert_filename=cls._getenv('CERT_FILENAME'),
            use_ci_job_token=cls._getenv('USE_CI_JOB_TOKEN', required=False, default=False, cast=utils.cast_bool),  # noqa: E501
            gitlab_bearer_token=cls._getenv('GITLAB_BEARER_TOKEN', required=False),
        )

    @classmethod
    def _getenv(cls, *key_names, required=True, default=None, cast=str):
        for name in key_names:
            val = os.getenv(name)
            if val is not None:
                return cast(val)
        if required:
            raise envparse.ConfigurationError(
                f"Please set the environment variable '{key_names[0]}'"
            )
        else:
            return default


class DownloadPrevCertCommand:
    def __init__(self, logger, config: DownloadPrevCertConfig):
        def false_to_none(value):
            if value is False:
                return None
            else:
                return value

        utils.check_one_of_two_config_options_set(
            'USE_CI_JOB_TOKEN', false_to_none(config.use_ci_job_token),
            'GITLAB_BEARER_TOKEN', config.gitlab_bearer_token
        )

        if config.use_ci_job_token and os.getenv('CI_JOB_TOKEN') is None:
            raise envparse.ConfigurationError(
                'When USE_CI_JOB_TOKEN is enabled, the environment variable CI_JOB_TOKEN' +
                ' must be set.'
            )

        self.logger = logger
        self.config = config

    def run(self):
        self.logger.info('Downloading Gitlab API artifact: %s', self._url())
        resp = requests.get(self._url(), headers=self._auth_header())

        if resp.status_code == 404:
            self.logger.info('Artifact not found.')
            sys.exit(30)
        if resp.status_code != 200:
            self.logger.error("Gitlab API returned error: HTTP code %s", resp.status_code)
            self.logger.error("API response body: %s", resp.text)
            raise utils.AbortException()

        self.logger.info('Storing artifact into %s', self.config.cert_filename)
        with open(self.config.cert_filename, 'wb') as f:
            f.write(resp.content)

    def _url(self):
        c = self.config
        project = self._urlencode(c.project_path)
        branch = self._urlencode(c.branch_name)
        filename = self._urlencode(c.cert_filename)
        job = self._urlencode(c.requester_job_name)
        return f"{c.gitlab_api_v4_url}/projects/{project}/jobs/artifacts/{branch}/raw/{filename}?job={job}"  # noqa: E501

    def _auth_header(self):
        if self.config.use_ci_job_token:
            return {'JOB-TOKEN': os.getenv('CI_JOB_TOKEN')}
        else:
            return {'Authorization': f"Bearer {self.config.gitlab_bearer_token}"}

    def _urlencode(self, value):
        return urllib.parse.quote(value).replace('/', '%2F')


def main():
    try:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
        config = DownloadPrevCertConfig.from_env()
        command = DownloadPrevCertCommand(logging.getLogger(), config)
    except envparse.ConfigurationError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    try:
        command.run()
    except utils.AbortException:
        sys.exit(1)


if __name__ == '__main__':
    main()
