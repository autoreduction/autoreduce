from setuptools import setup

setup(name='AutoReduction',
      version='1.0',
      description='ISIS AutoReduction service',
      author='ISIS Autoreduction Team',
      url='https://github.com/ISISScientificComputing/autoreduce/',
      install_requires=[
          'Django==1.11.12',
          'django_extensions==2.0.7',
          'django-user-agents==0.3.2',
          'MySQL-python==1.2.5',
          'python-daemon==2.1.2',
          'requests==2.18.4',
          'SQLAlchemy==1.2.7',
          'stomp.py==4.1.20',
          'suds==0.4',
          'Twisted==14.0.2',
          'watchdog==0.8.3'
      ]
      )
