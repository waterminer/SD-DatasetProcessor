from setuptools import setup, find_packages

setup(
    name='dataset_processor',
    version='0.3.0',
    packages=['dataset_processor', 'dataset_processor.tools'],
    url='https://github.com/waterminer/SD-DatasetProcessor',
    license='GPLv3',
    author='Water_miner',
    author_email='420773173@qq.com',
    description='A dataset preprocess toolkit',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: GPU :: NVIDIA CUDA :: 11.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.10',
    ],
)

