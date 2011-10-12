%define name ajenti
%define version 0.5_13.1
%define unmangled_version 0.5-13.1
%define unmangled_version 0.5-13.1
%define release 1

Summary: The server administration panel
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: LGPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Eugeny Pankov <e@ajenti.org>
Url: http://ajenti.org/

requires: gevent, python-lxml, python-pyOpenSSL, python-feedparser

%description
Web admin panel

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
