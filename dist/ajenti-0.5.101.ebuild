# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=4
PYTHON_DEPEND="2:2.6"
SUPPORT_PYTHON_ABIS=1

inherit distutils

DESCRIPTION="Web toolset for administrating servers"
HOMEPAGE="http://ajenti.org/"
SRC_URI="http://repo.ajenti.org/src/${P}.tar.gz"

LICENSE="LGPL-3"
KEYWORDS="~amd64 ~x86"
SLOT="0"
IUSE=""

RDEPEND="dev-python/feedparser
	dev-python/gevent
	dev-python/lxml
	dev-python/pyopenssl"

RESTRICT_PYTHON_ABIS="2.4 2.5 3.*"