PKGNAME=loopia-dynamic-dns

install:
	# Create log and config directory
	install -dm755 $(DESTDIR)/var/log/${PKGNAME}
	install -dm755 $(DESTDIR)/etc/${PKGNAME}
	# Copy other files to their locations, also world-readable
	install -Dm644 update.py $(DESTDIR)/opt/${PKGNAME}/update.py
	install -Dm644 config.py $(DESTDIR)/opt/${PKGNAME}/config.py
	install -Dm644 logger.py $(DESTDIR)/opt/${PKGNAME}/logger.py
	install -Dm644 LICENSE $(DESTDIR)/usr/share/licenses/${PKGNAME}/LICENSE
