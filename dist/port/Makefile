# New ports collection makefile for:   ajenti
# Date created:        15 October 2011
# Whom:                eugeny
#
# $FreeBSD$
#

PORTNAME=	ajenti
PORTVERSION=	0.6.1
CATEGORIES=	sysutils
MASTER_SITES=	http://repo.ajenti.org/src/

MAINTAINER=	e@ajenti.org
COMMENT=	Web toolset for server administration

LICENSE=	GPLv3

RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}gevent>=0.13.6:${PORTSDIR}/devel/py-gevent \
				${PYTHON_PKGNAMEPREFIX}openssl>=0.13:${PORTSDIR}/security/py-openssl \
				${PYTHON_PKGNAMEPREFIX}lxml>=2.3:${PORTSDIR}/devel/py-lxml

USE_PYTHON=		yes
USE_PYDISTUTILS=	easy_install
PYDISTUTILS_PKGNAME=	${PORTNAME}

.include <bsd.port.pre.mk>

post-patch:
	${REINPLACE_CMD} -e 's|/etc|/usr/local/etc|g;s|/var/lib/ajenti|${DATADIR}|g' \
		${WRKSRC}/setup.py ${WRKSRC}/${PORTNAME}-panel \
		${WRKSRC}/packaging/files/${PORTNAME}.conf ${WRKSRC}/${PORTNAME}/plugmgr.py \
		${WRKSRC}/${PORTNAME}/feedback.py

.include <bsd.port.post.mk>
