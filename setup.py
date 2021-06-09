import setuptools
import os.path

with open('README.md', 'r', encoding='UTF-8') as f:
    long_description = f.read()

version_txt_path = os.path.join('venafi_vcert_gitlab_integration', 'version.txt')
with open(version_txt_path, 'r', encoding='UTF-8') as f:
    version = f.read().strip()

setuptools.setup(
    name='venafi-vcert-gitlab-integration',
    version=version,
    license='Apache 2.0',
    author='Fullstaq',
    author_email='info@fullstaq.com',
    description='Venafi Machine Identity Management: Gitlab integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/fullstaq-labs/venafi-vcert-gitlab-integration",
    platforms='any',
    zip_safe=False,  # we require version.txt
    packages=['venafi_vcert_gitlab_integration'],
    package_data={
        'venafi_vcert_gitlab_integration': ['*.txt'],
    },
    entry_points={
        'console_scripts': [
            'venafi-vcert-version=venafi_vcert_gitlab_integration.version_command:main',  # noqa:E501
            'venafi-vcert-request-certificate=venafi_vcert_gitlab_integration.request_certificate_command:main',  # noqa:E501
            'venafi-vcert-download-prev-cert=venafi_vcert_gitlab_integration.download_prev_cert_command:main',  # noqa:E501
        ]
    },
    install_requires=[
        'vcert>=0.9.1,<0.10',
        'envparse>=0.2.0,<0.3',
        'requests>=2.25.1,<3',
        'cryptography>=3.4.7,<4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
