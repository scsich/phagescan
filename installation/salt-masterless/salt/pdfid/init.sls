# no special pkgs required for PDFiD other than python itself
# This state is simply to make it uniform with all other av engine states.
# It needs a single state so the engine install script can loop through
# engines in a uniform manner.
pdfid-reqts:
  cmd.run:
    - name: date