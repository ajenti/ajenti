# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3
PYTHON_DEPEND=2
SUPPORT_PYTHON_ABIS=1

inherit distutils

DESCRIPTION="Web toolset for administrating servers"
HOMEPAGE="http://ajenti.org/"
SRC_URI="http://repo.ajenti.org/src/${P}.tar.gz"

LICENSE="as-is LGPL-3"
KEYWORDS="~amd64 ~x86"
SLOT="0"
IUSE=""

DEPEND=""
RDEPEND="dev-python/gevent
	dev-python/lxml
	dev-python/pyopenssl
	dev-python/feedparser"

RESTRICT_PYTHON_ABIS="3.*"
