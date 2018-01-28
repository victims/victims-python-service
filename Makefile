.PHONY: help image

default: help

help:
	@echo "Targets:"
	@echo "	image: builds a container image"


image:
	sudo s2i build -E .s2i/environment . registry.access.redhat.com/rhscl/python-36-rhel7:latest victims-python
