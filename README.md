# Pluto Marine Watch v0.0.5

Python 3.10+, no third-party dependencies. Run `python -m pmw.server --demo --db data/demo.sqlite` and open http://127.0.0.1:8080. Tests: `python -m unittest discover -s tests -v`.

Synthetic own ship, three AIS-like targets, RMC/HDT, local plot, range/orientation, bearings and CPA/TCPA. Negative TCPA means past closest approach; CPA is constrained to future time. Not for navigation. No real radio or AIS input yet. Localhost only; no authentication. License not yet approved.

Network NMEA: `python -m pmw.server --nmea tcp://192.0.2.10:10110` (replace example IP with authorized gateway), or `--nmea udp://127.0.0.1:10110` (bind to configured local interface). Demo and network modes are exclusive. Position and heading expire after 15 seconds. AIS and Signal K are pending.
