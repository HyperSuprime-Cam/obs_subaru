# Set up aperture photometry
# 'root' should be a SourceMeasurementConfig

root.algorithms.names |= ["flux.aperture"]
# Roughly (1.0, 1.4, 2.0, 2.8, 4.0, 5.7, 8.0, 11.3, 16.0, 22.6 arcsec) in diameter: 2**(0.5*i)
# (assuming plate scale of 0.168 arcsec pixels)
root.algorithms["flux.aperture"].radii = [3.0, 4.5, 6.0, 9.0, 12.0, 17.0, 25.0, 35.0, 50.0, 70.0]

# Use a large aperture to be somewhat independent of seeing (used by ApFlux slot)
root.algorithms["flux.sinc"].radius = 12.0

# Use a large aperture for the flux used in calibration (the CalibFlux slot)
# We use flux.naive for that because we expect we don't need the sinc algorithm for
# large apertures.  If we make this too much smaller, we should switch it to a
# re-registration of flux.sinc (in meas_algorithms).
# For applying the curve of growth, this should also be listed in the root.algorithms["flux.aperture"].radii
root.algorithms["flux.naive"].radius = 12.0
