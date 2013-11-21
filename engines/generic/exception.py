

class UnsupportedFileTypeForScanner(Exception):
	message = "Unsupported Filetype For Scanner"


class ScannerCantParseFile(Exception):
	pass


class ScannerConnectionError(Exception):
	pass


class ScannerMustSpecifyInfectionName(Exception):
	pass


class ScannerRequiresLicenseFile(Exception):
	"""
	Thrown when the scanner requires a license file, e.g. Kaspersky's .key file, but this file is not present.
	"""
	pass


class ScannerLacksSufficientPermissions(Exception):
	"""
	Thrown when a scan adapter is unable to complete its duties due to insufficient permissions.
	"""
	pass


class ScannerOutputFileToBeSavedMustBeFullPath(Exception):
	pass


class ScannerUpdateError(Exception):
	"""
	Thrown when scanner's update_definitions() function returns an error.
	Anything other than a successful update or update is unnecessary.
	"""
	pass


class ScannerNotInstalled(Exception):
	"""
	Thrown when a scan engine is trying to be called, but it is not installed.
	"""
	pass
