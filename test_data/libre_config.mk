# Dummy Configuration

# This is a comment

# Another comment

# Define some variables
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
LIBDIR=$(PREFIX)/lib
INCLUDEDIR=$(PREFIX)/include

# Define some targets
all:
	@echo "Building all targets"

clean:
	@echo "Cleaning up"

install:
	@echo "Installing files"

# End of file