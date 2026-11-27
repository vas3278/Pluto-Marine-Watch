# Pluto Marine Watch v0.0.4

Python 3.10+, no third-party dependencies. Run `python -m pmw.server --demo --db data/demo.sqlite` and open http://127.0.0.1:8080. Tests: `python -m unittest discover -s tests -v`.

Synthetic own ship, three AIS-like targets, RMC/HDT, local plot, range/orientation, bearings and CPA/TCPA. Negative TCPA means past closest approach; CPA is constrained to future time. Not for navigation. No real radio, AIS or NMEA input yet. Localhost only; no authentication. License not yet approved.
