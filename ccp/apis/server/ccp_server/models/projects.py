# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from ccp.apis.server.ccp_server.models.base_model_ import Model
from ccp.apis.server.ccp_server.models.meta import Meta  # noqa: F401,E501
from ccp.apis.server.ccp_server.models.project import Project  # noqa: F401,E501
from ccp.apis.server.ccp_server import util


class Projects(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, meta: Meta = None,
                 projects: List[Project] = None):  # noqa: E501
        """Projects - a model defined in Swagger

        :param meta: The meta of this Projects.  # noqa: E501
        :type meta: Meta
        :param projects: The projects of this Projects.  # noqa: E501
        :type projects: List[Project]
        """
        self.swagger_types = {
            'meta': Meta,
            'projects': List[Project]
        }

        self.attribute_map = {
            'meta': 'meta',
            'projects': 'projects'
        }

        self._meta = meta
        self._projects = projects

    @classmethod
    def from_dict(cls, dikt) -> 'Projects':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Projects of this Projects.  # noqa: E501
        :rtype: Projects
        """
        return util.deserialize_model(dikt, cls)

    @property
    def meta(self) -> Meta:
        """Gets the meta of this Projects.


        :return: The meta of this Projects.
        :rtype: Meta
        """
        return self._meta

    @meta.setter
    def meta(self, meta: Meta):
        """Sets the meta of this Projects.


        :param meta: The meta of this Projects.
        :type meta: Meta
        """

        self._meta = meta

    @property
    def projects(self) -> List[Project]:
        """Gets the projects of this Projects.


        :return: The projects of this Projects.
        :rtype: List[Project]
        """
        return self._projects

    @projects.setter
    def projects(self, projects: List[Project]):
        """Sets the projects of this Projects.


        :param projects: The projects of this Projects.
        :type projects: List[Project]
        """

        self._projects = projects
