import setuptools

with open('README.md', 'r', encoding='UTF-8') as f:
    long_description = f.read()

setuptools.setup(
    name='venafi-vcert-gitlab-integration',
    version='0.9.0',
    license='Apache 2.0',
    author='Fullstaq',
    author_email='info@fullstaq.com',
    description='Venafi Machine Identity Protection: Gitlab integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/fullstaq-labs/venafi-vcert-gitlab-integration",
    platforms='any',
    packages=['venafi_vcert_gitlab_integration'],
    entry_points={
        'console_scripts': [
            'venafi-vcert-request-certificate=venafi_vcert_gitlab_integration.request_certificate_command:main',  # noqa:E501
        ]
    },
    install_requires=[
        'vcert>=0.9.1,<0.10',
        'envparse>=0.2.0,<0.3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
