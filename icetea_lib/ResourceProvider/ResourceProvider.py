"""
Copyright 2017 ARM Limited
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

ResourceProvider module. Handling of allocations and resource configurations is done here.
"""

import icetea_lib.LogManager as LogManager
from icetea_lib.ResourceProvider.exceptions import ResourceInitError
from icetea_lib.ResourceProvider.Allocators.exceptions import AllocationError
from icetea_lib.tools.tools import Singleton


class ResourceProvider(object):
    """
    Singleton ResourceProvider class. ResourceProvider is common for the entire run and it
    handles allocation of resources based on requested resource configurations. It also
    determines which allocator is used for allocating these resources.
    """
    __metaclass__ = Singleton

    def __init__(self, args):
        # @TODO: Refactor args into some separate configuration class maybe?
        self.args = args
        self.allocator = None
        self.jsonconf = None
        no_file = False if self.args.list or self.args.listsuites else True
        self.logger = LogManager.get_resourceprovider_logger("ResourceProvider", "RSP", no_file)
        self._pluginmanager = None

    def set_pluginmanager(self, pluginmanager):
        self._pluginmanager = pluginmanager

    def __del__(self):
        if self.allocator:
            self.allocator.cleanup()
            self.allocator = None

    def resolve_configuration(self, conf, resource_configuration):
        """
        Resolve the configuration from given JSON encoded configuration data.

        :param conf: JSON encoded configuration
        :param resource_configuration: ResourceConfig object
        """
        if not self.logger:
            self.logger = LogManager.get_resourceprovider_logger("ResourceProvider", "RSP")
        self.jsonconf = conf
        resource_configuration.resolve_configuration(conf)

    def allocate_duts(self, resource_configuration):
        """
        Initialize DUT's.

        :param resource_configuration: ResourceConfig
        :return: List of DUT objects
        :raises: ResourceInitError
        """
        cnt_hrdwr = resource_configuration.count_hardware()
        if not self.allocator:
            self.allocator = self.__get_allocator()
        try:
            # Try to allocate resources and instantiate DUT's
            dut_conf_list = resource_configuration.get_dut_configuration()
            if dut_conf_list:
                self.logger.debug("Allocating duts with the following configurations:")
                for conf in dut_conf_list:
                    self.logger.debug(conf.get_requirements())
            self.logger.info("Allocating {} duts.".format(resource_configuration.count_duts()))
            allocations = self.allocator.allocate(resource_configuration, args=self.args)
            self.logger.info("Allocation successful")
        except AllocationError as error:
            raise ResourceInitError(error.message)

        return allocations

    def cleanup(self):
        """
        Clean up allocator at the end of the run.

        :return: Nothing
        """
        self.logger.debug("Cleaning up ResourceProvider.")
        if self.allocator:
            self.logger.debug("Cleaning up allocator.")
            self.allocator.cleanup()

    def __get_allocator(self):
        """
        Internal method for determining which allocator is needed for this run.

        :return: BaseAllocator
        :raises: ResourceInitError
        """
        allocator_name = self.args.allocator
        allocator = self._pluginmanager.get_allocator(allocator_name)
        if allocator is None:
            raise ResourceInitError("Unable to load allocator {}".format(allocator_name))
        self.logger.debug("Using allocator %s", allocator_name)
        return allocator(self.args, None)

    def get_my_duts(self):
        """
        Get my duts.

        :return: list of duts
        """
        # TODO: Is this function still used somewhere? There are no usages in this project at least.
        if self.args.my_duts:
            myduts = self.args.my_duts.split(',')
            return myduts
        return None
