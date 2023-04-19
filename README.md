# FRAM
MicroPython class for interacting with Ferroelectric Random Access Memory (MB85RS2MTA)

This was developed on Pi PICO, using hardware SPI and the SPI library from MicroPython.

SpiRam is a class that allows easy read/write access to the great FRAM chip.
These chips provide fantastic speed of read and write, and amazing data retention times (>200 years!!!)

Ver 1 
peek and poke opearations on bytearrays are supported.
lock and unlock of write is supported
simple fast search function has been started, more work will be done

