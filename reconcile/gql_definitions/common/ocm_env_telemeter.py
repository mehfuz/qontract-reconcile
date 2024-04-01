"""
Generated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!
"""
from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611
from datetime import datetime  # noqa: F401 # pylint: disable=W0611
from enum import Enum  # noqa: F401 # pylint: disable=W0611
from typing import (  # noqa: F401 # pylint: disable=W0611
    Any,
    Optional,
    Union,
)

from pydantic import (  # noqa: F401 # pylint: disable=W0611
    BaseModel,
    Extra,
    Field,
    Json,
)

from reconcile.gql_definitions.fragments.prometheus_instance import PrometheusInstance


DEFINITION = """
fragment PrometheusInstance on PrometheusInstance_v1 {
  name
  description
  baseUrl
  queryPath
  auth {
    provider
    ... on PrometheusInstanceBearerAuth_v1 {
      token {
        ... VaultSecret
      }
    }
    ... on PrometheusInstanceOidcAuth_v1 {
      accessTokenClientId
      accessTokenUrl
      accessTokenClientSecret {
        ... VaultSecret
      }
    }
  }
}

fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query OCMEnvTelemeter($name: String) {
  ocm_envs: ocm_environments_v1(name: $name) {
    name
    telemeter {
      ... PrometheusInstance
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union=True
        extra=Extra.forbid


class OpenShiftClusterManagerEnvironmentV1(ConfiguredBaseModel):
    name: str = Field(..., alias="name")
    telemeter: Optional[PrometheusInstance] = Field(..., alias="telemeter")


class OCMEnvTelemeterQueryData(ConfiguredBaseModel):
    ocm_envs: list[OpenShiftClusterManagerEnvironmentV1] = Field(..., alias="ocm_envs")


def query(query_func: Callable, **kwargs: Any) -> OCMEnvTelemeterQueryData:
    """
    This is a convenience function which queries and parses the data into
    concrete types. It should be compatible with most GQL clients.
    You do not have to use it to consume the generated data classes.
    Alternatively, you can also mime and alternate the behavior
    of this function in the caller.

    Parameters:
        query_func (Callable): Function which queries your GQL Server
        kwargs: optional arguments that will be passed to the query function

    Returns:
        OCMEnvTelemeterQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return OCMEnvTelemeterQueryData(**raw_data)
