.. _setup-devenv-build-tools:

Build tools
***********

This setup is required for the development of the :ref:`Core <setup-devenv-core>` and the :ref:`Extension plugins <setup-devenv-extension-plugins>`.


Steps
-----

Install Curl::

    sudo apt install curl

Install NodeJS - you can use the NodeSource repositories for quick setup::

    # Using Ubuntu
    curl -sL https://deb.nodesource.com/setup_17.x | sudo -E bash -
    sudo apt-get install -y nodejs

    # Using Debian, as root
    curl -sL https://deb.nodesource.com/setup_17.x | bash -
    apt-get install -y nodejs

    # Using RHEL or centos, as root
    curl -sL https://rpm.nodesource.com/setup_17.x | bash -

Install Yarn - Enable the official Yarn repository, import the repository GPG key, and install the package.::

    # Using Ubuntu
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update
    sudo apt install --no-install-recommends yarn

Install Angular CLI::

    sudo yarn global add @angular/cli

Install Gettext::

    # Ubuntu or Debian:
    sudo apt-get install gettext

    # RHEL or CentOS
    dnf install gettext


Install Ajenti Dev Multitool::

    pip3 install ajenti-dev-multitool

(More info about the :ref:`Ajenti Dev Multitool <dev-multitool>`)
