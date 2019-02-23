from setuptools import setup

setup(name='yatapi',
      version='0.1',
      description='Yet Another Trigger API (YATAPI) is a Python based generator of SCMDraft TrigEdit triggers '
                  'featuring type annotations, autocompletion, and one-to-one correspondence with TrigEdit triggers.',
      url='https://github.com/sethmachine/yatapi',
      author='sethmachine',
      author_email='sethmachine01@gmail.com',
      license='MIT',
      install_requires=[],
      packages=['yatapi'],
      # package_dir={'org.mitre.nlp.mbv':'org/mitre/nlp/mbv'},
      # package_data={'pyw3x':['data/storm/*.*', 'data/storm/win-64/*.*']},
      zip_safe=False)

