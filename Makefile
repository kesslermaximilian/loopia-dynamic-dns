PKGNAME=loopia-dynamic-dns

install:
	# Create log directory
	install -dm755 $(DESTDIR)/var/log/${PKGNAME}
	# Create config directory. This should not be accessible by world, since it will contain
	# the credentials for the loopia API.
	# Make sure this is later owned by the user executing the update script
	install -dm700 $(DESTDIR)/etc/${PKGNAME}
	# Copy other files to their locations, also world-readable
	install -Dm644 update.py $(DESTDIR)/opt/${PKGNAME}/update.py
	install -Dm644 config.py $(DESTDIR)/opt/${PKGNAME}/config.py
	install -Dm644 logger.py $(DESTDIR)/opt/${PKGNAME}/logger.py
	install -Dm644 LICENSE $(DESTDIR)/usr/share/licenses/${PKGNAME}/LICENSE
