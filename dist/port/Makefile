# New ports collection makefile for:   ajenti
# Date created:        15 October 2011
# Whom:                eugeny
#
# $FreeBSD$
#

PORTNAME=      ajenti
PORTVERSION=   0.5.101
CATEGORIES=    sysutils
MASTER_SITES=  http://repo.ajenti.org/bsd/

MAINTAINER=    e@ajenti.org
COMMENT=       Web toolset for server administration

RUN_DEPENDS= \
	${NONEXISTENT}:${PORTSDIR}/devel/py-gevent \
	${NONEXISTENT}:${PORTSDIR}/devel/py-greenlet \
	${NONEXISTENT}:${PORTSDIR}/security/py-openssl \
	${NONEXISTENT}:${PORTSDIR}/textproc/py-feedparser \
	${NONEXISTENT}:${PORTSDIR}/devel/py-lxml

USE_PYTHON=    yes

.include <bsd.port.mk>
