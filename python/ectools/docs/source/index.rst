Welcome to ectools documentation!
=================================
**ectools** is a collection of helper modules for EFEC testing. It works fine under python 2.7.x and python 3.5.x.

Overview
--------
.. image:: _static/ectools.png

Installation
------------
You may already have ectools installed -- you can check by doing::

    python -c "import ectools"

To install or update to latest version, please run below command::

    pip install ectools -U --extra-index-url http://jenkins.englishtown.com:8081/pypi --trusted-host jenkins.englishtown.com

Additional requirements for Ubuntu/Debian::

    sudo apt-get install freetds-dev

Additional requirements for Mac OS X with homebrew::

    brew install homebrew/versions/freetds091

Get Started
-----------
The first step you should do is settiing up ectools, you should specify which environment and partner that you are working on::

    from ectools.config import setup, set_environment, set_partner

    # setup for both
    setup(env='UAT', partner='Cool')

    # setup environment only
    set_environment('QA')

    # setup partner only
    set_partner('Mini')
 
By default, it is pointing to **UAT** and **Cool** if you didn't specify anything. Please note, the ``env`` and ``partner`` will be cached in runtime once being set, you can change them by call above method multiple times. 

.. note::

  The setting value is case-insenstive, so 'uat', 'UAT' and 'Uat' are all acceptable, same as 'mini' and 'MINI'.

The next step is importing a helper that you want, and call the methods it provides, for example::

    from ectools.account_helper import activate_account

    # activate a test account according to environment and partner
    account = activate_account()
    print(account['member_id'])  # get its info

    # activate a test account with more parameters
    account = activate_account(product_id=63, school_name='SH_BBB', startLevel=12)

    for k, v in account.items():
        print("{0}=>{1}".format(k, v))  # get all detail

If you have your own defined class to present a `Student`, you can convert the above `account` to your object like this::

    from ectools.account_helper import activate_account, convert_account_to_object
    from my.objects import Student, School

    account = activate_account()
    student = convert_account_to_object(account, account_object_type=Student, school_object_type=School)

    # now it is good to use your object attributes
    print(student.member_id)
    print(student.school.name)

To explore more in **ectools**, please check each module from content table by yourself.
  
Module Content
--------------
.. toctree::
  :maxdepth: 2

  ectools

Looking for Help?
-----------------
If you have any issue or feedback, please contact EFEC QA Team<ec_qa@ef.com>, or find Toby Qin on Skype.