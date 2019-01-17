Changelog
=========

0.5 (unreleased)
----------------

- Nothing changed yet.


0.4.2 (2019-01-17)
------------------

- Fix POSKeyError when calculating file size.


0.4.1 (2018-04-27)
------------------

- ImageScaling view should not throw an error if called without anything.


0.4 (2018-03-15)
----------------

- Fix unicode errors.
- Fix check for form groups.


0.3 (2017-11-29)
----------------

- Clean up old scales when image changes.
- Code cleanup (fixed code-analysis errors).


0.2 (2015-02-13)
----------------

- Fix url generation for widget downloads/previews.
- Fix unicode errors for filenames.
- Keep uploaded files/images on form reload.


0.1.4 (2012-01-21)
------------------

- Return None if we can't handle the image file.
- Permission problems with secured context. RSP for the moment...


0.1.3 (2011-06-05)
------------------

- Fixed wrong 'Modified-Since' header generation (now uses zope.datetime).


0.1.2 (2011-06-05)
------------------

- Respond with 304 (not modified) if request contains 'If-Modiefied-Since' header and image was not modified.


0.1.1 (2011-02-27)
------------------

- Added utils module containing scale and tag functions.
- Small bugfixes.
